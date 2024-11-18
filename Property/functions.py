from .models import Stage
from django.utils import timezone

def update_stage(opportunity, stage_name):
    try:
        stage = Stage.objects.get(stage=stage_name)
        opportunity.stage = stage
        opportunity.in_listed_stage_since = timezone.now()
        opportunity.save()
    except Exception as e:
        print(f'Error at updatre_stage: {e}')