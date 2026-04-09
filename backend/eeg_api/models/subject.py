from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import AuditBaseModel
from django.conf import settings

class SubjectProfile(AuditBaseModel):
    
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')

    identifier = models.CharField(max_length=100, unique=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subject_profile'
    )
    
    firstname = models.CharField(max_length=150, blank=True, null=True)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    
    gender = models.CharField(
        max_length=2, 
        choices=Gender.choices, 
        blank=True, 
        null=True
    ) 

    class Meta:
        db_table = 'SubjectProfile'

    def __str__(self):
        if self.lastname and self.firstname:
            return f"{self.identifier} - {self.lastname}, {self.firstname}"
        return self.identifier

class SubjectProfileInfoCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'SubjectProfileInfoCategory'

    def __str__(self):
        return self.name

class SubjectProfileInfo(AuditBaseModel):
    subject = models.ForeignKey(SubjectProfile, on_delete=models.CASCADE, related_name='profile_infos', null=True)
    category = models.ForeignKey(SubjectProfileInfoCategory, on_delete=models.PROTECT, null=True, blank=True)
    
    title = models.CharField(max_length=200, default="Allgemeine Info")
    description = models.TextField()

    class Meta:
        db_table = 'SubjectProfileInfo'

    def __str__(self):
        sub_id = self.subject.identifier if self.subject else "Unassigned"
        return f"{sub_id} - {self.title}"