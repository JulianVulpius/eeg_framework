from django.db import models
from .base import AuditBaseModel
from .component import Component

class PageCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'PageCategory'

    def __str__(self):
        return self.name

class Page(AuditBaseModel):
    class Scope(models.TextChoices):
        ALL = 'ALL', 'All (Subject & Admin)'
        SUBJECT = 'SUBJECT', 'Subject Only'
        ADMIN = 'ADMIN', 'Admin Only'

    name = models.CharField(max_length=150)
    category = models.ForeignKey(PageCategory, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.ALL)
    
    components = models.ManyToManyField(
        Component, 
        through='PageComponent',
        related_name='pages'
    )

    class Meta:
        db_table = 'Page'

    def __str__(self):
        return f"{self.name} ({self.get_scope_display()})"

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