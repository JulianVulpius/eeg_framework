from django.db import models
from .base import AuditBaseModel
from .subject import SubjectProfile

class MedicalHistoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'MedicalHistoryCategoy'

    def __str__(self):
        return self.name

class MedicalHistory(AuditBaseModel):
    category = models.ForeignKey(MedicalHistoryCategory, on_delete=models.PROTECT)
    description = models.TextField()

    # The 'through' parameter tells Django to use your specific junction table below
    subjects = models.ManyToManyField(
        SubjectProfile, 
        through='SubjectMedicalHistory',
        related_name='medical_histories'
    )

    class Meta:
        db_table = 'MedicalHistory'

    def __str__(self):
        return f"Medical History: {self.category.name}"

class SubjectMedicalHistory(models.Model):
    """
    Explicit relation table mapping Subjects to their Medical Histories.
    """
    subject = models.ForeignKey(SubjectProfile, on_delete=models.CASCADE)
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE)

    class Meta:
        # This forces the database table name to be exactly what you want in DBeaver
        db_table = 'SubjectProfile_MedicalHistory'
        
        # Ensures a subject can't have the exact same medical history record linked twice
        unique_together = ('subject', 'medical_history')

    def __str__(self):
        return f"{self.subject.identifier} - {self.medical_history.category.name}"