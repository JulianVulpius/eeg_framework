from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from eeg_api.models.metadata import EntityMetaDataRegistry, MetaDataDefinition, MetaDataGroup, MetaDataGroupDefinition, MetaDataValue, MetaDataGroupInstance

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']

class EntityMetaDataRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityMetaDataRegistry
        fields = ['id', 'target_table', 'allowed_category', 'description', 'is_active']

class MetaDataDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaDataDefinition
        fields = ['id', 'category', 'name', 'description', 'expected_data_type']

class MetaDataGroupSerializer(serializers.ModelSerializer):
    definitions = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    assigned_definitions = serializers.SerializerMethodField(read_only=True)

    def validate_name(self, value):
        query = MetaDataGroup.objects.filter(name__iexact=value.strip())
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("A Metadata Group with this name already exists.")
        return value.strip()

    class Meta:
        model = MetaDataGroup
        fields = ['id', 'category', 'name', 'description', 'definitions', 'assigned_definitions']

    def get_assigned_definitions(self, obj):
        mgds = MetaDataGroupDefinition.objects.filter(group=obj).order_by('order')
        return [mgd.definition.id for mgd in mgds]

    def create(self, validated_data):
        definitions_data = validated_data.pop('definitions', [])
        group = MetaDataGroup.objects.create(**validated_data)
        for index, def_id in enumerate(definitions_data):
            definition = MetaDataDefinition.objects.get(id=def_id)
            MetaDataGroupDefinition.objects.create(
                group=group, 
                definition=definition, 
                order=index + 1 
            )
        return group

    def update(self, instance, validated_data):
        definitions_data = validated_data.pop('definitions', None)
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        if definitions_data is not None:
            MetaDataGroupDefinition.objects.filter(group=instance).delete()
            for index, def_id in enumerate(definitions_data):
                definition = MetaDataDefinition.objects.get(id=def_id)
                MetaDataGroupDefinition.objects.create(
                    group=instance, 
                    definition=definition, 
                    order=index + 1
                )
        return instance

class MetaDataValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaDataValue
        fields = ['id', 'definition', 'value']

class MetaDataValueWriteSerializer(serializers.ModelSerializer):
    """ Used strictly for saving new values """
    class Meta:
        model = MetaDataValue
        fields = ['definition', 'value']

class MetaDataGroupInstanceSerializer(serializers.ModelSerializer):
    values = MetaDataValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = MetaDataGroupInstance
        fields = ['id', 'group', 'creation_source', 'content_type', 'object_id', 'values', 'created_at']
        read_only_fields = ['created_at', 'creation_source']