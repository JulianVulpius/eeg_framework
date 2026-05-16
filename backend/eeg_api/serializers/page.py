from rest_framework import serializers
from eeg_api.models import Page, PageCategory, PageGroup, PageGroupCategory, Component, PageComponent, PageGroupPage

class PageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PageCategory
        fields = '__all__'

class PageSerializer(serializers.ModelSerializer):
    components = serializers.PrimaryKeyRelatedField(
        queryset=Component.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Page
        fields = ['id', 'name', 'category', 'description', 'scope', 'components']

    def create(self, validated_data):
        components_data = validated_data.pop('components', [])
        page = Page.objects.create(**validated_data)
        for index, comp in enumerate(components_data):
            PageComponent.objects.create(page=page, component=comp, order=index + 1)
        return page

    def update(self, instance, validated_data):
        if 'components' in validated_data:
            components_data = validated_data.pop('components')
            PageComponent.objects.filter(page=instance).delete()
            for index, comp in enumerate(components_data):
                PageComponent.objects.create(page=instance, component=comp, order=index + 1)
        
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.scope = validated_data.get('scope', instance.scope)
        instance.save()
        return instance

class PageGroupCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PageGroupCategory
        fields = '__all__'

class PageGroupSerializer(serializers.ModelSerializer):
    pages = serializers.PrimaryKeyRelatedField(
        queryset=Page.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = PageGroup
        fields = ['id', 'name', 'category', 'description', 'pages']

    def create(self, validated_data):
        pages_data = validated_data.pop('pages', [])
        group = PageGroup.objects.create(**validated_data)
        for index, page in enumerate(pages_data):
            PageGroupPage.objects.create(page_group=group, page=page, order=index + 1)
        return group

    def update(self, instance, validated_data):
        if 'pages' in validated_data:
            pages_data = validated_data.pop('pages')
            PageGroupPage.objects.filter(page_group=instance).delete()
            for index, page in enumerate(pages_data):
                PageGroupPage.objects.create(page_group=instance, page=page, order=index + 1)
                
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance