import json
from django.shortcuts import render
from .functions import update_stage, update_sub_stage, process_note
from .models import Opportunity, Note
from django.shortcuts import render, get_object_or_404

def view_opportunities(request):
    try:
        opportunities = Opportunity.objects.all()
        return render(request, 'viewMulti.html', {'opportunities': opportunities})
    except Exception as e:
        print('Error at view_opportunities: {e}')


def view_opportunity(request, id):
    try:
        opportunity = get_object_or_404(Opportunity, pk=id)
        if request.method == "GET":
            # Get related notes
            notes = Note.objects.filter(opportunity = opportunity).order_by('-pk')
            return render(request, 'viewSingle.html', {
                'opportunity': opportunity,
                'notes': notes
            })
        if request.method == "POST":
            logged_in_user = request.user
            request_data = json.loads(request.body)
            action = request_data.get('action')
            if action == 'stageUpdate':
                # Return will pass update status to client device
                return update_stage(opportunity, request_data.get('stage'))
            if action == 'subStageUpdate':
                return update_sub_stage(opportunity, request_data.get('subStageName'), request_data.get('value'), request_data.get('inputId'))
            if action == 'actionNote':
                return process_note(logged_in_user, opportunity, request_data.get('actionType'), request_data.get('title'), request_data.get('value'), request_data.get('noteId'))

    except Exception as e:
        print('Error at view_opportunities: {e}')
