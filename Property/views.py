from django.shortcuts import render
from .models import Property, Opportunity

def view_opportunities(request):
    # GET REQUEST
    if request.method == "GET":
        opportunities = Opportunity.objects.all()
        return render(request, 'viewMulti.html', {'opportunities': opportunities})
    # POST REQUEST
