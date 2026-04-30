from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .base import AuditBaseModel

class MetaDataCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'MetaDataCategory'

    def __str__(self):
        return self.name

class MetaDataDefinition(AuditBaseModel):
    # Restricts what types of data the frontend should expect
    class DataType(models.TextChoices):
        STRING = 'STRING', 'String / Text'
        INTEGER = 'INTEGER', 'Integer Number'
        FLOAT = 'FLOAT', 'Floating Point Number'
        BOOLEAN = 'BOOLEAN', 'True / False'
        JSON = 'JSON', 'JSON Object'

    category = models.ForeignKey(MetaDataCategory, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    expected_data_type = models.CharField(
        max_length=20, 
        choices=DataType.choices, 
        default=DataType.STRING
    )

    class Meta:
        db_table = 'MetaDataDefinition'

    def __str__(self):
        return f"{self.name} ({self.expected_data_type})"

class MetaDataGroupCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'MetaDataGroupCategory'

    def __str__(self):
        return self.name

class MetaDataGroup(AuditBaseModel):
    category = models.ForeignKey(MetaDataGroupCategory, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    definitions = models.ManyToManyField(
        MetaDataDefinition, 
        through='MetaDataGroupDefinition',
        related_name='groups'
    )

    class Meta:
        db_table = 'MetaDataGroup'

    def __str__(self):
        return self.name

class MetaDataGroupDefinition(models.Model):
    group = models.ForeignKey(MetaDataGroup, on_delete=models.CASCADE)
    definition = models.ForeignKey(MetaDataDefinition, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'MetaDataGroup_MetaDataDefinition'
        ordering = ['order']
        unique_together = ('group', 'order')

    def __str__(self):
        return f"{self.group.name} - {self.definition.name} (Pos: {self.order})"

class MetaDataGroupInstance(AuditBaseModel):
    class CreationSource(models.TextChoices):
        MANUAL = 'MANUAL', 'Manual Registry Assignment'
        COMPONENT = 'COMPONENT', 'Automated Component / Session'
        DEVICE = 'DEVICE', 'Device Settings / Specs'

    group = models.ForeignKey(MetaDataGroup, on_delete=models.PROTECT)
    
    creation_source = models.CharField(
        max_length=20,
        choices=CreationSource.choices,
        default=CreationSource.MANUAL
    )
    
    # acts as EntityType_ID
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # acts as Entity_ID
    object_id = models.PositiveIntegerField()
    # combines them into a single queryable object in Python
    parent_entity = GenericForeignKey('content_type', 'object_id')
    # ----------------------------------------

    class Meta:
        db_table = 'MetaDataGroupInstance'

    def __str__(self):
        return f"Instance of {self.group.name} ({self.creation_source}) for {self.content_type.model} ID {self.object_id}"

class MetaDataValue(models.Model):
    # No audit base needed here because the parent Instance already tracks when the form was created/changed
    # related_name='values' in MetaDataValue is a handy Django trick. If we fetch a MetaDataGroupInstance we can instantly get all its answered questions by typing instance.values.all().
    instance = models.ForeignKey(MetaDataGroupInstance, on_delete=models.CASCADE, related_name='values')
    definition = models.ForeignKey(MetaDataDefinition, on_delete=models.PROTECT)
    
    # Using TextField to ensure it can hold long strings or stringified JSON if needed
    value = models.TextField()

    class Meta:
        db_table = 'MetaDataValue'

    def __str__(self):
        return f"{self.definition.name}: {self.value}"

class EntityMetaDataRegistry(AuditBaseModel):
    """
    Dictates which database tables are allowed to use which MetaDataGroupCategories.
    """
    # points to a specific table (e.g., DeviceInstance, SubjectProfile)
    target_table = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    
    # points to the allowed category of templates (e.g., "Hardware Settings", "Clinical Questionnaires")
    allowed_category = models.ForeignKey(MetaDataGroupCategory, on_delete=models.CASCADE)
    
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('target_table', 'allowed_category')
        db_table = 'EntityMetaDataRegistry'

    def __str__(self):
        return f"{self.target_table.model} -> {self.allowed_category.name}"