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
        print(f'updating {sub_stage} to {value}')
        # Get the current value for the substage before update
        current_val = getattr(opportunity, sub_stage)
        if current_val == None or current_val == 'NA':
            audit_log_msg = f'{user_friendly_substage_name} set as {value}'
        else:
            audit_log_msg = f'{user_friendly_substage_name} updated from {current_val} to {value}'
        # Format Yes/No as boolean
        if sub_stage == 'hardcopy_docs_requested':
            value = False if value == 'No' else True
        # Format empty date 
        if sub_stage == 'contracts_issued_to_purchaser' or sub_stage == 'contracts_received_date' or sub_stage == 'deposit_received_date':
            if not value:
                value = None
        setattr(opportunity, sub_stage, value)
        opportunity.save()
        return JsonResponse ({'message': audit_log_msg}, status = 200)
    except Exception as e:
        return JsonResponse ({'status': 'Error occurred with stage update'}, status = 500)