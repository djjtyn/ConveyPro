from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Stage, Note, LocalDocument
from Auth.models import CustomUser
from django.utils import timezone
import os

def update_stage(opportunity, stage_name):
    try:
        #Get existing stage
        current_stage = opportunity.stage
        updated_stage =  Stage.objects.get(stage=stage_name)
        opportunity.stage = updated_stage
        opportunity.in_listed_stage_since = timezone.now()
        opportunity.save()
        audit_log_msg = f'Stage updated from {current_stage} to {updated_stage}'
        return JsonResponse ({'message': audit_log_msg}, status = 200)
    except Exception as e:
        return JsonResponse ({'status': 'Error occurred with stage update'}, status = 500)
    
def update_sub_stage(opportunity, sub_stage, value, user_friendly_substage_name):
    try:
        # Get the current value for the substage before update
        current_val = getattr(opportunity, sub_stage)
        # Determine if increment/decriment of sub stage counter is required
        completed_counter_action = determine_completed_counter_action(current_val, value)
        # Create a dynamic audit message
        audit_log_msg = create_log_msg(current_val, user_friendly_substage_name, value)
        #The value may need to be formatted prior to entering db
        value = format_value(sub_stage, value)
        setattr(opportunity, sub_stage, value)
        opportunity.save()
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
    #Dont need to consider prior value as it was empty 
    if current_val == None or current_val == 'NA':
        return f'{user_friendly_substage_name} set as {value}'
    #Prior value added to audit message
    return f'{user_friendly_substage_name} updated from {current_val} to {value}'

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
    
def upload_files(opportunity, files):
    status = 'Upload Error'
    try:
        if os.environ['CLOUD_STORAGE'] == 'False':
            use_local_storage = True
        file_counter = 0
        file_tracker = []
        for file in files:
            if use_local_storage:
                stored_file = LocalDocument(name = file.name, size = file.size, opportunity=opportunity, file = file)
            stored_file.save()
            file_obj = {
                'id': stored_file.id,
                'name': stored_file.name,
                'url': stored_file.file.url
            }
            file_tracker.append(file_obj)
            file_counter+=1
        status = f'{file_counter} Files Uploaded' if file_counter > 1 else 'File Uploaded'
        return JsonResponse (
            {
                'message': status,
                'files': file_tracker
            }, status = 200)
    except Exception as e:
        print(f'Error at create note: {e}')
        return JsonResponse ({'message': status}, status = 500)
    
def delete_document(document_id):
    status = 'Error deleting document'
    try:
        if os.environ['CLOUD_STORAGE'] == 'False':
            use_local_storage = True
        if use_local_storage:
            document = LocalDocument.objects.get(pk=document_id)
            document.delete_file()
        document.delete()
        status = 'Document Deleted'
        return JsonResponse ({'message': status}, status = 200)
    except Exception as e:
        print(f'Error at delete_document: {e}')
        return JsonResponse ({'message': status}, status = 500)


