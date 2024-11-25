from datetime import datetime
import os
from django.db import models
from django.conf import settings
from django.utils import timezone

class Stage(models.Model):
    stage = models.CharField(max_length = 100)

    def __str__(self):
        return self.stage

class Country(models.Model):
    country = models.CharField(max_length=255)

    def __str__(self):
        return self.country

class Development(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='client')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='agent')

class Property(models.Model):
    name = models.CharField(max_length=255)
    bedroom_amount = models.SmallIntegerField(null = True)
    development = models.ForeignKey('Development', on_delete = models.SET_NULL, null = True)

    #Address Fields
    address_line_one = models.CharField(max_length=255)
    address_line_two = models.CharField(max_length=255)
    address_line_three = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)
    country = models.ForeignKey('Country', on_delete = models.SET_NULL, null = True)

    def get_formatted_address(self):
        # Properties may not have all propery address fields populated so custom address format is required 
        address = ''
        #Only target the address fields of the model
        address_fields = ['address_line_one', 'address_line_two', 'address_line_three', 'city', 'postcode', 'country']
        for field in self._meta.get_fields(include_parents=True):
            if field.name in address_fields:
                address += f'{getattr(self, field.name, None)}, '
        # Remove last ',' character and space in the return
        return address[:-2]
    
    # Function outputs class used in css for JS bed filter to determine visibility
    def get_formatted_bedroom_amount(self):
        return f'{self.bedroom_amount}Bed'

    def __str__(self):
        return self.name
    
    def output_bedroom_amount(self):
        return f'{self.bedroom_amount} Bed'

#Document will extend to account for both local stored and hosted documents
class Document(models.Model):
    name = models.CharField(max_length = 400)
    size = models.IntegerField(null=True)
    opportunity = models.ForeignKey('Opportunity', on_delete = models.SET_NULL, null = True)


    class Meta:
        abstract = True

class LocalDocument(Document):
    file = models.FileField(upload_to='uploads/')

    def delete_file(self):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)

class HostedDocument(Document):
    document_url = models.TextField()

class Note(models.Model):
    title =  models.CharField(max_length = 400)
    content = models.TextField(max_length=1000, null=True)
    created_at = models.DateTimeField(null = False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='created_by')
    modified_at = models.DateTimeField(null = False)
    modifed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='modified_by')
    opportunity = models.ForeignKey('Opportunity', on_delete = models.SET_NULL, null = True)

    def __str__(self):
        return self.title

class Opportunity(models.Model):
    stage = models.ForeignKey('Stage', on_delete = models.SET_NULL, null = True)
    property = models.ForeignKey("Property", on_delete = models.SET_NULL, null=True)
    purchaser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='purchaser')
    solicitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='solicitor')
    in_listed_stage_since = models.DateTimeField(null = False)
    last_modified_date = models.DateTimeField(auto_now_add=True, null = True)
    contracts_issued_to_purchaser = models.DateTimeField(null = True, blank = True)
    hardcopy_docs_requested = models.BooleanField(null=True, blank = True)
    precontract_queries_received_date = models.CharField(max_length = 50, null = True, blank = True)
    precontract_queries_response_date = models.CharField(max_length = 50, null = True, blank = True)
    chaser_email_one_send_date = models.CharField(max_length = 50, null = True, blank = True)
    rejoinders_received_date = models.CharField(max_length = 50, null = True, blank = True)
    rejoinders_response_date = models.CharField(max_length = 50, null = True, blank = True)
    chaser_email_two_send_date = models.CharField(max_length = 50, null = True, blank = True)
    further_rejoinders_received_date = models.CharField(max_length = 50, null = True, blank = True)
    further_rejoinders_response_date = models.CharField(max_length = 50, null = True, blank = True)
    contracts_received_date = models.DateTimeField(null = True, blank = True)
    deposit_received_date = models.DateTimeField(null = True, blank = True)
    closing_requirements_received_date = models.DateTimeField(null = True, blank = True)
    closing_requirements_returned_date = models.DateTimeField(null = True, blank = True)
    title_deed_send_date = models.DateTimeField(null = True, blank = True)

    def get_days_in_stage_amount(self):
        delta = timezone.now() - self.in_listed_stage_since
        return delta.days
    
    def get_last_modified_date(self):
        return self.last_modified_date.strftime('%d/%m/%Y')

    # This method is used to determine what class to give the opportunity item in the viewMulti HTML page
    def getIdleStageTimeRange(self):
        idleDays = self.get_days_in_stage_amount()
        if idleDays <= 13:
            return 'idleTimeStageOne'
        elif idleDays <= 21:
            return 'idleTimeStageTwo'
        else:
            return 'idleTimeStageThree'
        
    def are_hardcopy_docs_requested(self):
        if self.hardcopy_docs_requested:
            return True
        return False
    
    #Count how many sub stage attributees within the Sale Agreed stage are populates
    def get_sale_agreed_substage_complete_count(self):
        substage_fields = [
            'contracts_issued_to_purchaser', 'precontract_queries_received_date', 'precontract_queries_response_date',  
            'chaser_email_one_send_date', 'rejoinders_received_date', 'rejoinders_response_date', 'chaser_email_two_send_date', 'further_rejoinders_received_date',
             'further_rejoinders_response_date', 'contracts_received_date', 'deposit_received_date'
        ]
        # Start at 1 to account for hardcopy_docs_requested boolean field
        count = 1
        for stage in substage_fields:
            val = getattr(self, stage, None)
            if val:
                count+=1
        return count
    
        #Count how many sub stage attributees within the Sale Agreed stage are populates
    def get_contracts_exchanged_substage_complete_count(self):
        substage_fields = ['closing_requirements_received_date', 'closing_requirements_returned_date', 'title_deed_send_date']
        count = 0
        for stage in substage_fields:
            val = getattr(self, stage, None)
            if val:
                count+=1
        return count
    
    def __str__(self):
        return self.property.name


     


