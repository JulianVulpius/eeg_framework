from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import AuditBaseModel

class SubjectProfile(AuditBaseModel):
    
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')

    # identifier stays mandatory (unique)
    identifier = models.CharField(max_length=100, unique=True)
    
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
        # fallback if names are not provided
        if self.lastname and self.firstname:
            return f"{self.identifier} - {self.lastname}, {self.firstname}"
        return self.identifier