from django.db import models

# Create your models here.
class Contact_Master(models.Model):
    cont_id =models.AutoField(primary_key=True)
    Name=models.CharField(max_length=30)
    Email=models.CharField(max_length=20)
    Mobile=models.CharField(max_length=12)
    Feedback=models.CharField(max_length=1000)