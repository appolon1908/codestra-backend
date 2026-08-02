import uuid
from django.db import models
from django.conf import settings 


def generate_id():
    return uuid.uuid4().hex


class HeaderTitle(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    page = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    



class CaseStudy(models.Model):
    title = models.CharField(max_length=256)
    descriptiion = models.TextField()
    image = models.FileField(upload_to="cms/images")
    
    def __str__(self):
        return self.title
    

class FAQs(models.Model):
    question = models.CharField(max_length=256)
    answer = models.TextField()
    
    
class ContactUs(models.Model):
    full_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)
    company_size = models.CharField(max_length=20, null=True, blank=True)
    message = models.TextField()
    
    def __str__(self):
        return self.full_name
    
    

class Logo(models.Model):
    logo = models.ImageField(upload_to="logo/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
class TaxPayer(models.Model):
    #Campo que hace la relacion entre un usuario y el taxpayer:
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tax_payers')

    address_reference = models.CharField(max_length=256, null=True, blank=True)
    visiting_hours = models.CharField(max_length=256, null=True, blank=True)
    
    # Legal representation
    representation_rnc = models.CharField(max_length=256, null=True, blank=True)
    name_of_representative = models.CharField(max_length=256, null=True, blank=True)
    representative_phone = models.CharField(max_length=256, null=True, blank=True)
    representative_cell_phone = models.CharField(max_length=256, null=True, blank=True)
    representative_email = models.CharField(max_length=256, null=True, blank=True)
    media_file = models.FileField(upload_to="tax/image", null=True, blank=True)
    operation_carried_out_in_premise = models.CharField(max_length=256, null=True, blank=True)
    
    # store or warehouse data
    street_of_warehouse = models.CharField(max_length=256, null=True, blank=True) 
    store_or_warehouse_number = models.CharField(max_length=256, null=True, blank=True) 
    province_of_warehouse = models.CharField(max_length=256, null=True, blank=True) 
    warehouse_reference = models.CharField(max_length=256, null=True, blank=True) 
    local_administration = models.CharField(max_length=256, null=True, blank=True) 
    warehouse_sector = models.CharField(max_length=256, null=True, blank=True)
    
    tax_payer_rnc = models.CharField(max_length=256, null=True, blank=True)
    name_of_tax_payer = models.CharField(max_length=256, null=True, blank=True) 
    trade_name = models.CharField(max_length=256, null=True, blank=True)
    tax_payer_telephone = models.CharField(max_length=256, null=True, blank=True)
    tax_payer_cell_phone = models.CharField(max_length=256, null=True, blank=True)
    tax_payer_email = models.CharField(max_length=256, null=True, blank=True)
    tax_payer_number = models.CharField(max_length=256, null=True, blank=True)
    tax_payer_sector = models.CharField(max_length=256, null=True, blank=True)
    tax_payer_province = models.CharField(max_length=256, null=True, blank=True)

    
    
    
class Testimonial(models.Model):
    pass