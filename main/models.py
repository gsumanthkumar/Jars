from pyexpat import model
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    is_recruiter = models.BooleanField(default=False)
    is_jobseeker = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Job(models.Model):
    role = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    salary = models.BigIntegerField()
    recruiter = models.ForeignKey(User,on_delete=models.CASCADE)
    posted_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Application(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    resume = models.FileField()
    applicant = models.ForeignKey(User,on_delete=models.CASCADE)
    status = models.BooleanField(null=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)