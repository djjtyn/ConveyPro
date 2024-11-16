from django.db import models
from django.conf import settings

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
    
    def __str__(self):
        return self.name
    
    def output_bedroom_amount(self):
        return f'{self.bedroom_amount} Bed'

class Document(models.Model):
    name = models.CharField(max_length = 400)
    size = models.IntegerField(null=True)
    document_url = models.TextField()
    opportunity = models.ForeignKey('Opportunity', on_delete = models.SET_NULL, null = True)

class Note(models.Model):
    title =  models.CharField(max_length = 400)
    content = models.TextField(max_length=1000, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='created_by')
    modifed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='modified_by')
    opportunity = models.ForeignKey('Opportunity', on_delete = models.SET_NULL, null = True)

class Opportunity(models.Model):
    stage = models.ForeignKey('Stage', on_delete = models.SET_NULL, null = True)
    property = models.ForeignKey("Property", on_delete = models.SET_NULL, null=True)
    purchaser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='purchaser')
    solicitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name='solicitor')
    in_listed_stage_since = models.DateTimeField(auto_now_add=True, null = True)
     


