from django.db import models

# Create your models here.

class User(models.Model):
    gender=(
        ('male',"男"),
        ("female","女"),
    )
    username=models.CharField(max_length=128,unique=True)
    email=models.EmailField(unique=True)
    sex=models.CharField(max_length=32,choices=gender,default="男")
    password=models.CharField(max_length=20)


