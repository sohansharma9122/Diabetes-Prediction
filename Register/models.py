from django.db import models

# Create your models here.
class Register_Master(models.Model):
    reg_id =models.AutoField(primary_key=True)
    Name=models.CharField(max_length=30)
    Email=models.CharField(max_length=20,unique=True)
    Mobile=models.CharField(max_length=12)
    Password=models.CharField(max_length=15)
    Gender=models.CharField(max_length=10)
    DOB=models.DateField(max_length=20)
    Address=models.CharField(max_length=30)
    

    def __str__(self):
        return self.Name