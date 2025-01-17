import json
from django.shortcuts import redirect, render
from .functions import update_stage, update_sub_stage, process_note, upload_files, delete_document, get_overview_data
from .models import Development, Opportunity, Note, LocalDocument, HostedDocument, ChangeAudit
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import os

def redirect_to_opportunities(request):
    return redirect('property:view_opportunities', development = 'all')

@login_required
def view_opportunities(request, development = None):
    try:
        if development and development != 'all':
            opportunities = Opportunity.objects.select_related('property').select_related('stage').filter(property__development__formatted_url_name=development)
        else:
            opportunities = Opportunity.objects.all()
        return render(request, 'viewMulti.html', {
            'opportunities': opportunities,
            'development': development
            }
        )
    except Exception as e:
        print(f'Error at view_opportunities: {e}')

@login_required
def view_opportunity(request,development, id):
    try:
        opportunity = get_object_or_404(Opportunity, pk=id)
        if request.method == "GET":
            # Get related notes
            notes = Note.objects.filter(opportunity = opportunity).order_by('-pk')
            # Get related documents
            if os.environ['CLOUD_STORAGE'] == 'False':
                documents = LocalDocument.objects.filter(opportunity = opportunity).order_by('-pk')
            else:
                documents = HostedDocument.objects.filter(opportunity = opportunity).order_by('-pk')
            # Get Audit logs
            audit_history = ChangeAudit.objects.filter(opportunity = opportunity).order_by('-pk')
            return render(request, 'viewSingle.html', {
                'opportunity': opportunity,
                'notes': notes,
                'documents': documents,
                'development': development,
                'audit_history': audit_history
            })
        if request.method == "POST":
            # Returns will pass update status to client device
            logged_in_user = request.user
            #Document Upload
            if 'files' in request.FILES:
                files = request.FILES.getlist('files')
                return upload_files(logged_in_user, opportunity, files)
            request_data = json.loads(request.body)
            action = request_data.get('action')
            if action == 'deleteDocument':
                return delete_document(logged_in_user, opportunity, request_data.get('docId'))
            if action == 'stageUpdate':
                return update_stage(logged_in_user, opportunity, request_data.get('stage'))
            if action == 'subStageUpdate':
                return update_sub_stage(logged_in_user, opportunity, request_data.get('subStageName'), request_data.get('value'), request_data.get('inputId'))
            if action == 'actionNote':
                return process_note(logged_in_user, opportunity, request_data.get('actionType'), request_data.get('title'), request_data.get('value'), request_data.get('noteId'))
    except Exception as e:
        print('Error at view_opportunity: {e}')

@login_required
def view_overview(request, development):
    try:
        if development and development != 'all':
             opportunities = Opportunity.objects.select_related('stage').filter(property__development__formatted_url_name=development)
        # All opportunities can be retrieved 
        else: 
            opportunities = Opportunity.objects.select_related('stage').all()
        total_amount= len(opportunities)
        if development == 'all':
            development_label = 'All Developments'
        else:
            developmentObj = Development.objects.get(formatted_url_name = development)
            development_label = developmentObj.name
        #Init a dict containing compounded opportunity data
        overviewObj = get_overview_data(opportunities, total_amount)
        return render(request, 'overview.html', {
            'overviewObj': overviewObj,
            'development': development,
            'developmentLabel': development_label
            }
        )
    except Exception as e:
        print(f'Error at view_overview(): {e}')