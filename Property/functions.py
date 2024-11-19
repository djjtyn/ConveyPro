from django.http import JsonResponse
from .models import Stage
from django.utils import timezone

def update_stage(opportunity, stage_name):
    try:
        #Get existing stage
        current_stage = opportunity.stage
        updated_stage = stage = Stage.objects.get(stage=stage_name)
        opportunity.stage = updated_stage
        opportunity.in_listed_stage_since = timezone.now()
        opportunity.save()
        audit_log_msg = f'Stage updated from {current_stage} to {updated_stage}'
        return JsonResponse ({'message': audit_log_msg}, status = 200)
    except Exception as e:
        return JsonResponse ({'status': 'Error occurred with stage update'}, status = 500)