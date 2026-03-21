from django.db import models
from .base import AuditBaseModel

class CustomScriptCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'CustomScriptCategory'

    def __str__(self):
        return self.name

class CustomScriptLanguage(models.Model):
    name = models.CharField(max_length=50) 
    version = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'CustomScriptLanguage'

    def __str__(self):
        return f"{self.name} {self.version if self.version else ''}".strip()

class CustomScript(AuditBaseModel):
    category = models.ForeignKey(CustomScriptCategory, on_delete=models.PROTECT)
    language = models.ForeignKey(CustomScriptLanguage, on_delete=models.PROTECT)
    
    source = models.TextField(help_text="File path or raw script code")
    
    # JSONField fir flexible configurations
    # default=dict ensures it defaults to an empty JSON object {} rather than NULL
    parameter = models.JSONField(default=dict, blank=True, help_text="Default JSON parameters for the script")

    class Meta:
        db_table = 'CustomScript'

    def __str__(self):
        return f"Script: {self.id} ({self.language.name})"

# -----------------------------------------------------------------------------
# DATA PROCESS (Analysis Pipelines)
# -----------------------------------------------------------------------------
class DataProcessCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'DataProcessCategory'

    def __str__(self):
        return self.name

class DataProcess(models.Model):
    category = models.ForeignKey(DataProcessCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    scripts = models.ManyToManyField(
        CustomScript, 
        through='DataProcessCustomScript',
        related_name='data_processes'
    )

    class Meta:
        db_table = 'DataProcess'

    def __str__(self):
        return self.name

class DataProcessCustomScript(models.Model):
    data_process = models.ForeignKey(DataProcess, on_delete=models.CASCADE)
    custom_script = models.ForeignKey(CustomScript, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'DataProcess_CustomScript'
        ordering = ['order']
        unique_together = ('data_process', 'order')

    def __str__(self):
        return f"{self.data_process.name} - Script {self.custom_script.id} (Pos: {self.order})"

# -----------------------------------------------------------------------------
# DATA DISPLAY (Visualization Pipelines)
# -----------------------------------------------------------------------------
class DataDisplayCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'DataDisplayCategory'

    def __str__(self):
        return self.name

class DataDisplay(models.Model):
    category = models.ForeignKey(DataDisplayCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    scripts = models.ManyToManyField(
        CustomScript, 
        through='DataDisplayCustomScript',
        related_name='data_displays'
    )

    class Meta:
        db_table = 'DataDisplay'

    def __str__(self):
        return self.name

class DataDisplayCustomScript(models.Model):
    data_display = models.ForeignKey(DataDisplay, on_delete=models.CASCADE)
    custom_script = models.ForeignKey(CustomScript, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'DataDisplay_CustomScript'
        ordering = ['order']
        unique_together = ('data_display', 'order')

    def __str__(self):
        return f"{self.data_display.name} - Script {self.custom_script.id} (Pos: {self.order})"