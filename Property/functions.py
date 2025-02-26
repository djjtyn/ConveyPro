from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import HostedDocument, Stage, Note, LocalDocument, ChangeAudit, ChangeType
from Auth.models import CustomUser
from django.utils import timezone
from azure.storage.blob import BlobServiceClient
import os

def update_stage(logged_in_user, opportunity, stage_name):
    try:
        #Get existing stage
        current_stage = opportunity.stage
        updated_stage =  Stage.objects.get(stage=stage_name)
        opportunity.stage = updated_stage
        opportunity.in_listed_stage_since = timezone.now()
        opportunity.save()
        audit_log_msg = f'Stage updated from {current_stage} to {updated_stage}'
        create_audit_record(opportunity, audit_log_msg, logged_in_user, 'Stage')
        return JsonResponse ({'message': audit_log_msg}, status = 200)
    except Exception as e:
        return JsonResponse ({'status': 'Error occurred with stage update'}, status = 500)
    
def update_sub_stage(logged_in_user, opportunity, sub_stage, value, user_friendly_substage_name):
    try:
        print(value)
        # Get the current value for the substage before update
        current_val = getattr(opportunity, sub_stage)
        # Determine if increment/decriment of sub stage counter is required
        completed_counter_action = determine_completed_counter_action(current_val, value)
        # Create a dynamic audit message
        audit_log_msg = create_log_msg(current_val, user_friendly_substage_name, value)
        print(audit_log_msg)
        #The value may need to be formatted prior to entering db
        value = format_value(sub_stage, value)
        setattr(opportunity, sub_stage, value)
        opportunity.save()
        create_audit_record(opportunity, audit_log_msg, logged_in_user, 'Substage')
        return JsonResponse ({
            'message': audit_log_msg,
            'renderCount': completed_counter_action
            }, status = 200
        )
    except Exception as e:
        print(f'Error at update_sub_stage: {e}')
        return JsonResponse ({'status': 'Error occurred with stage update'}, status = 500)
    
def determine_completed_counter_action(value, update_value):
    if value == None:
        return 'increment'
    if value and update_value:
        return 'static'
    return 'decrement'

def create_log_msg(current_val, user_friendly_substage_name, value):
    # Create user friendly date format for updated value if required
    value = format_date_value_if_required(value, '%Y-%m-%d')
    #Dont need to consider prior value as it was empty 
    if current_val == None or current_val == 'NA':
        return f'{user_friendly_substage_name} set as {value}'
    # Create user friendly date format for prior value if required
    current_val = format_date_value_if_required(current_val, '%Y-%m-%d %H:%M:%S')
    return f'{user_friendly_substage_name} updated from {current_val} to {value}'

def format_date_value_if_required(input, initialFormat):
    # If input is already a date there is no need to conver it to a date
    if isinstance(input, datetime):
        return input.strftime("%d/%m/%Y")
    try:
        date_obj = datetime.strptime(input, initialFormat)
        return date_obj.strftime("%d/%m/%Y")
    except:
        return input

def format_value(sub_stage, value):
    # Format Yes/No as boolean
    if sub_stage == 'hardcopy_docs_requested':
         value = False if value == 'No' else True
    # Format empty date 
    if is_static_date_input(sub_stage):
        if not value:
            value = None
    return value

def is_static_date_input(sub_stage):
    static_inputs = [
        'contracts_issued_to_purchaser', 'contracts_received_date', 'deposit_received_date', 
        'closing_requirements_received_date', 'closing_requirements_returned_date', 'title_deed_send_date'
    ]
    return sub_stage in static_inputs

def process_note(logged_in_user,opportunity, action_type, title, content, note_id=None):
    try:
        if action_type == 'delete':
            note_status = delete_note(note_id)
            render_note_counter = 'decrement'
        #if valid note id is passed, update the note 
        if action_type == 'update':
            note_status = update_note(note_id, title,content, logged_in_user)
            render_note_counter = 'static'
        if action_type == 'create':   
            #if no note id exists create a new note 
            note_status,note_id = create_note(opportunity, title,content, logged_in_user)
            render_note_counter = 'increment'
        create_audit_record(opportunity,  note_status, logged_in_user, 'Note')
        return JsonResponse ({
            'message': note_status,
            'renderCount': render_note_counter,
            'affectedNoteId': note_id
            }, status = 200
        )
    except Exception as e:
        print(f'Error at process_note: {e}')

def delete_note(note_id):
    update_status = 'Error deleting Note'
    try:
        note = Note.objects.get(pk=note_id)
        note.delete()
        update_status = 'Note Deleted'
        return update_status
    except Exception as e:
        print(f'Error at delete_note: {e}')
        return update_status

def update_note(id, title,content, logged_in_user):
    update_status = 'Error updating Note'
    try:
        note = get_object_or_404(Note, pk=id)
        if note:
            updated = False
            if title != note.title:
                note.title = title
                updated = True
            if content != note.content:
                note.content = content
                updated = True
            if updated:
                note.modifed_by = logged_in_user
                note.modified_at = timezone.now()
                note.save() 
                update_status = 'Note Updated'
        return update_status
    except Exception as e: 
        print(f'Error at update_note: {e}')
        return update_status
    
def create_note(opportunity, title,content, logged_in_user):
    update_status = 'Error creating Note'
    try:
        note = Note(
            title = title, content = content, created_at = timezone.now(), created_by = logged_in_user,modified_at = timezone.now(), modifed_by = logged_in_user, opportunity = opportunity
        )
        note.save()
        update_status = 'Note Created'
        return update_status, note.id
    except Exception as e:
        print(f'Error at create note: {e}')
        return update_status 
    
def upload_files(logged_in_user, opportunity, files):
    status = 'Upload Error'
    try:
        if os.environ['CLOUD_STORAGE'] == 'False':
            use_local_storage = True
        else:
            #Init BlobServiceClient to interact with Azure storage
            blob_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONN_STRING'])
            #Format the property development name so it can be used to create/identify blob container
            formatted_development = opportunity.property.get_development().lower().replace(' ', '')
            blob_container_client = get_blob_container(blob_client, formatted_development)
            blob_storage_root = os.environ['BLOB_STORAGE_ROOT']
            opportunity_id = opportunity.id
        file_counter = 0
        file_tracker = []
        for file in files:
            if use_local_storage:
                #Create LocalDocument Record
                stored_file = LocalDocument(name = file.name, size = file.size, opportunity=opportunity, file = file)
            else:
                # Upload file to Azure Blob storage and return its url
                upload_url = upload_blob_to_azure(blob_client, blob_container_client, file.name, opportunity_id, formatted_development, file, blob_storage_root)
                #Create HostedDocument Record
                stored_file = HostedDocument(name = file.name, size = file.size, opportunity=opportunity, document_url = upload_url)
            stored_file.save()
            file_obj = {
                'id': stored_file.id,
                'name': stored_file.name,
            }
            file_obj['url'] = stored_file.file.url if use_local_storage else upload_url
            file_tracker.append(file_obj)
            file_counter+=1
        status = f'{file_counter} Files Uploaded' if file_counter > 1 else 'File Uploaded'
        create_audit_record(opportunity, status, logged_in_user, 'Document')
        return JsonResponse (
            {
                'message': status,
                'files': file_tracker
            }, status = 200)
    except Exception as e:
        print(f'Error at create note: {e}')
        return JsonResponse ({'message': status}, status = 500)

def get_blob_container(blob_client, formatted_development):
    # Retrieve blob container which matches formatted development name. Create new container if none found
    container = blob_client.get_container_client(formatted_development)
    if not container.exists():
        container = blob_client.create_container(name=formatted_development)
    return container

def upload_blob_to_azure(blob_client, blob_container_client, file_name, opportunity_id, formatted_development, file, blob_storage_root):
    try:
        # Format uploaded file name to prevent any duplicate file names in blob container
        valid_file_name = generate_valid_upload_file_name(blob_client, file_name, opportunity_id, formatted_development)
        blob_container_client.upload_blob(name = valid_file_name, data = file)
        return f'{blob_storage_root}/{formatted_development}/{valid_file_name}'
    except Exception as e:
        print(f'Error at upload_blob_to_azure: {e}')

def generate_valid_upload_file_name(blob_client, file_name, opportunity_id, formatted_development):
    try:
        # Isolate both the file name and its type
        file_components = file_name.split('.')
        file_name = file_components[0]
        file_ext = file_components[1]
        #If a identical file name already exists in the storage container increment number after file name to avoid duplicate fiel names 
        file_index = 0
        #Start with assumption the file name already exists in container
        preexisting_filename = True
        while preexisting_filename:
            # file index only needs to be considered if a new file name needs to be generated
            if file_index > 0:
                file_identifier = f'Opp{opportunity_id}-{file_name}({file_index}).{file_ext}'
            else:
                file_identifier = f'Opp{opportunity_id}-{file_name}.{file_ext}'
            blob_file_reference = blob_client.get_blob_client(container = formatted_development, blob = file_identifier)
            #If filename already exists in container increment number at end of name, otherwise break out of loop
            if blob_file_reference.exists():
                file_index+=1
            else:
                preexisting_filename = False
        return file_identifier 
    except Exception as e:
        print(f'Error creating valid file name for Azure file upload: {e}')

def delete_document(logged_in_user, opportunity, document_id):
    status = 'Error deleting document'
    try:
        if os.environ['CLOUD_STORAGE'] == 'False':
            use_local_storage = True
        if use_local_storage:
            document = LocalDocument.objects.get(pk=document_id)
            document.delete_file()
        else:
            document = HostedDocument.objects.get(pk=document_id)
            # Remove file from Azure Blob Storage
            blob_storage_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONN_STRING'])
            #Actual document name may differ from local DB reference so needs to be retrieved from blob location url 
            blob_name = document.document_url.split('/')[-1]
            #Format the property development name so it can be used to identify relevant blob container
            formatted_development = opportunity.property.get_development().lower().replace(' ', '')
            blob_client = blob_storage_client.get_blob_client(container=formatted_development, blob = blob_name)
            blob_client.delete_blob()
        document.delete()
        status = 'Document Deleted'
        create_audit_record(opportunity, status, logged_in_user, 'Document')
        return JsonResponse ({'message': status}, status = 200)
    except Exception as e:
        print(f'Error at delete_document: {e}')
        return JsonResponse ({'message': status}, status = 500)
    
def get_overview_data(opportunities, total_amount):
    opp_obj = {
        'total_amount': total_amount
    }
    if opportunities:
        for_sale_amount = 0
        sale_agreed_amount = 0
        contracts_exchanged_amount = 0
        sold_amount = 0 
        idle_stage_one_amount = 0
        idle_stage_two_amount = 0
        idle_stage_three_amount = 0
        for opp in opportunities:
            if opp.stage.stage == "For Sale":
                for_sale_amount+=1
            if opp.stage.stage == "Sale Agreed":
                sale_agreed_amount +=1
                if opp.getIdleStageTimeRange() == 'idleTimeStageOne':
                    idle_stage_one_amount +=1
                elif opp.getIdleStageTimeRange() == 'idleTimeStageTwo':
                    idle_stage_two_amount +=1
                elif opp.getIdleStageTimeRange() == 'idleTimeStageThree':
                    idle_stage_three_amount +=1
            if opp.stage.stage == "Contracts Exchanged":
                contracts_exchanged_amount +=1
            if opp.stage.stage == "Sold":
                sold_amount +=1   
        opp_obj['for_sale_amount'] = for_sale_amount
        opp_obj['sale_agreed_amount'] = sale_agreed_amount
        opp_obj['contracts_exchanged_amount'] = contracts_exchanged_amount
        opp_obj['sold_amount'] = sold_amount
        if sale_agreed_amount > 0:
            opp_obj['idle_stage_one_amount_bar_percent_render'] = round((idle_stage_one_amount / sale_agreed_amount * 100) * 0.8) 
            opp_obj['idle_stage_two_amount_bar_percent_render'] = round((idle_stage_two_amount / sale_agreed_amount * 100) * 0.8)
            opp_obj['idle_stage_three_amount_bar_percent_render'] = round((idle_stage_three_amount / sale_agreed_amount * 100) * 0.8)
    return opp_obj

def create_audit_record(opportunity, details, user, type):
    try:
        record = ChangeAudit(details=details, opportunity = opportunity, made_by=user, change_type = ChangeType.objects.get(name=type))
        record.save()
    except Exception as e:
        print(f'Error at create_audit_record: {e}')