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