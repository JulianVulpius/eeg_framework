from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db.models import ProtectedError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ProtectedError):
        blocking_models = set()
        for obj in exc.protected_objects:
            blocking_models.add(obj._meta.verbose_name.title())
        
        models_str = ", ".join(blocking_models)
        
        return Response({
            "error_code": "PROTECTED_ERROR",
            "blocking_models": models_str,
            "detail": f"Locked by: {models_str}"
        }, status=status.HTTP_400_BAD_REQUEST)

    return response

from django.contrib.contenttypes.models import ContentType
from .models.metadata import MetaDataGroupInstance, MetaDataValue

def clone_metadata_group_instance(source_instance, target_object):
    """
    Clones a MetaDataGroupInstance and all associated MetaDataValues
    to a new target object.
    """
    if not source_instance:
        return None

    new_instance = MetaDataGroupInstance.objects.create(
        group=source_instance.group,
        creation_source=MetaDataGroupInstance.CreationSource.COMPONENT,
        content_type=ContentType.objects.get_for_model(target_object),
        object_id=target_object.id
    )

    for val in source_instance.values.all():
        MetaDataValue.objects.create(
            instance=new_instance,
            definition=val.definition,
            value=val.value
        )
    
    return new_instance