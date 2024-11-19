import json
from django.shortcuts import render
from .functions import update_stage
from .models import Property, Opportunity
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
            return render(request, 'viewSingle.html', {'opportunity': opportunity})
        if request.method == "POST":
            request_data = json.loads(request.body)
            action = request_data.get('action')
            if action == 'stageUpdate':
                # Return will pass update status to client device
                return update_stage(opportunity, request_data.get('stage'))
    except Exception as e:
        print('Error at view_opportunities: {e}')
