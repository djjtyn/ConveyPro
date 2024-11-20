from django.http import JsonResponse
from .models import Stage
from django.utils import timezone

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
