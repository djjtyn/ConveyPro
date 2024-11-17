from django.shortcuts import render
from .models import Property, Opportunity
from django.shortcuts import render, get_object_or_404

def view_opportunities(request):
    try:
        # GET REQUE
        if request.method == "GET":
            opportunities = Opportunity.objects.all()
            return render(request, 'viewMulti.html', {'opportunities': opportunities})
        # POST REQUEST

    except Exception as e:
        print('Error at view_opportunities: {e}')


def view_opportunity(request, id):
    try: 
        opportunity = get_object_or_404(Opportunity, pk=id)
        return render(request, 'viewSingle.html', {'opportunity': opportunity})
    except Exception as e:
        print('Error at view_opportunities: {e}')
