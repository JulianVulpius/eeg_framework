import django.utils.timezone
from typing import Optional

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from eeg_api.models import Session, MetaDataGroup, MetaDataGroupInstance, MetaDataValue, MetaDataDefinition
from eeg_api.serializers.session import SessionSerializer
from eeg_api.services.session_service import generate_blueprint, generate_report


class SessionViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for EEG sessions.
    Provides custom actions for generating UI blueprints and session reports.
    """
    serializer_class = SessionSerializer

    def get_queryset(self):
        queryset = Session.objects.all().order_by('-start_datetime')
        
        event = self.request.query_params.get('event')
        subject = self.request.query_params.get('subject')
        page_group = self.request.query_params.get('page_group')

        if event:
            queryset = queryset.filter(event_id=event)
        if subject:
            queryset = queryset.filter(subject_id=subject)
        if page_group:
            queryset = queryset.filter(page_group_id=page_group)
            
        return queryset

    def create(self, request: Request, *args, **kwargs) -> Response:
        event_id = request.data.get('event')
        subject_id = request.data.get('subject')
        page_group_id = request.data.get('page_group')
        location_id = request.data.get('location')
        start_datetime = request.data.get('start_datetime')

        session, created = Session.objects.get_or_create(
            event_id=event_id,
            subject_id=subject_id,
            page_group_id=page_group_id,
            defaults={
                'start_datetime': start_datetime,
                'location_id': location_id
            }
        )
        
        if not created:
            session.location_id = location_id
            session.start_datetime = start_datetime
            session.save()
        
        serializer = self.get_serializer(session)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def blueprint(self, request: Request, pk: Optional[int] = None) -> Response:
        """Builds a UI blueprint for the frontend runner."""
        session = self.get_object()
        scope = request.query_params.get('scope', 'ALL').upper()
        
        blueprint_data = generate_blueprint(session, scope)
        return Response(blueprint_data)

    @action(detail=True, methods=['post', 'put'])
    def save_metadata(self, request: Request, pk: Optional[int] = None) -> Response:
        """Saves metadata answers provided during the active session."""
        session = self.get_object()
        group_id = request.data.get('group_id')
        values = request.data.get('values', [])
        
        group = MetaDataGroup.objects.get(id=group_id)
        session_ct = ContentType.objects.get_for_model(Session)
        
        instance, created = MetaDataGroupInstance.objects.get_or_create(
            group=group,
            content_type=session_ct,
            object_id=session.id,
            defaults={'creation_source': MetaDataGroupInstance.CreationSource.COMPONENT}
        )
        
        for val in values:
            definition = MetaDataDefinition.objects.get(id=val['definition_id'])
            MetaDataValue.objects.update_or_create(
                instance=instance,
                definition=definition,
                defaults={'value': str(val['value'])}
            )
            
        return Response({"status": "success", "updated": not created})

    @action(detail=True, methods=['get'])
    def saved_metadata(self, request: Request, pk: Optional[int] = None) -> Response:
        """Retrieves currently saved metadata answers for the session."""
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        instances = MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        )
        
        # Flatten saved data into a dictionary
        saved_data = {
            val.definition.id: val.value 
            for inst in instances 
            for val in inst.values.all()
        }
                
        return Response(saved_data)
        
    @action(detail=True, methods=['post'])
    def reset(self, request: Request, pk: Optional[int] = None) -> Response:
        """Resets the session by deleting metadata and updating the start time."""
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        ).delete()
        
        session.start_datetime = django.utils.timezone.now()
        session.save()
        
        return Response({"status": "session_reset"})

    @action(detail=True, methods=['get'])
    def report(self, request: Request, pk: Optional[int] = None) -> Response:
        """Generates a complete summary report for the session, including uploaded files."""
        session = self.get_object()
        report_data = generate_report(session)
        return Response(report_data)