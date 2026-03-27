from django.db import models
from .base import AuditBaseModel
from .script import DataProcess, DataDisplay

class LocationCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'LocationCategory'

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(LocationCategory, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'Location'

    def __str__(self):
        return self.name

class ComponentType(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., 'Text Input Field'")
    
    # frontend uses this exact string to render the correct .vue file. 
    # it should never be changed once established (e.g., 'TEXT_INPUT', 'CUSTOM_DATA_DISPLAY').
    identifier = models.CharField(max_length=50, unique=True)
    
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ComponentType'

    def __str__(self):
        return f"{self.name} ({self.identifier})"


class ComponentCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ComponentCategory'

    def __str__(self):
        return self.name

class Component(AuditBaseModel):
    category = models.ForeignKey(ComponentCategory, on_delete=models.PROTECT, null=True, blank=True)
    component_type = models.ForeignKey(ComponentType, on_delete=models.PROTECT)
    
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    parameter = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'Component'

    def __str__(self):
        return f"{self.name} [{self.component_type.identifier}]"

class ComponentDataProcess(models.Model):
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    data_process = models.ForeignKey(DataProcess, on_delete=models.CASCADE)
    
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'DataProcess_Component'
        ordering = ['order']
        unique_together = ('component', 'order')

    def __str__(self):
        return f"{self.component.name} - Process: {self.data_process.name} (Pos: {self.order})"


class ComponentDataDisplay(models.Model):
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    data_display = models.ForeignKey(DataDisplay, on_delete=models.CASCADE)
    
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'DataDisplay_Component'
        ordering = ['order']
        unique_together = ('component', 'order')

    def __str__(self):
        return f"{self.component.name} - Display: {self.data_display.name} (Pos: {self.order})"

class PageCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'PageCategory'

    def __str__(self):
        return self.name

class Page(AuditBaseModel):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(PageCategory, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    components = models.ManyToManyField(
        Component, 
        through='PageComponent',
        related_name='pages'
    )

    class Meta:
        db_table = 'Page'

    def __str__(self):
        return self.name

class PageComponent(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'Page_Component'
        ordering = ['order']
        unique_together = ('page', 'order')

    def __str__(self):
        return f"{self.page.name} - {self.component.name} (Pos: {self.order})"

class EventCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'EventCategory'

    def __str__(self):
        return self.name

class Event(AuditBaseModel):
    name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(EventCategory, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    event_start = models.DateTimeField(null=True, blank=True)
    event_end = models.DateTimeField(null=True, blank=True)

    logo = models.ForeignKey('eeg_api.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='event_logos')
    poster = models.ForeignKey('eeg_api.MediaAsset', on_delete=models.SET_NULL, null=True, blank=True, related_name='event_posters')

    location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='events'
    )

    page_groups = models.ManyToManyField(
        'PageGroup', 
        through='EventPageGroup',
        related_name='events'
    )

    class Meta:
        db_table = 'Event'

    def __str__(self):
        return self.name

class EventGallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery')
    media = models.ForeignKey('eeg_api.MediaAsset', on_delete=models.CASCADE)
    display_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('event', 'media')
        ordering = ['display_order']
        db_table = 'Event_MediaAsset'

class PageGroupCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'PageGroupCategory'

    def __str__(self):
        return self.name

class PageGroup(AuditBaseModel):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(PageGroupCategory, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    pages = models.ManyToManyField(
        Page, 
        through='PageGroupPage',
        related_name='page_groups'
    )

    class Meta:
        db_table = 'PageGroup'

    def __str__(self):
        return self.name

class PageGroupPage(models.Model):
    page_group = models.ForeignKey(PageGroup, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'PageGroup_Page'
        ordering = ['order']
        unique_together = ('page_group', 'order')

    def __str__(self):
        return f"{self.page_group.name} - {self.page.name} (Pos: {self.order})"


class EventPageGroup(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    page_group = models.ForeignKey(PageGroup, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Event_PageGroup'
        unique_together = ('event', 'page_group') 

    def __str__(self):
        return f"{self.event.name} -> {self.page_group.name}"