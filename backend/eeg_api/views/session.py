from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import django.utils.timezone
from django.contrib.contenttypes.models import ContentType

from eeg_api.models.session import Session
from eeg_api.models.metadata import MetaDataGroup, MetaDataGroupInstance, MetaDataValue, MetaDataDefinition
from eeg_api.serializers.session import SessionSerializer

class SessionViewSet(viewsets.ModelViewSet):
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

    def create(self, request, *args, **kwargs):
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
        from rest_framework import status
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def blueprint(self, request, pk=None):
        session = self.get_object()
        pg = session.page_group

        scope = request.query_params.get('scope', 'ALL').upper()
        
        blueprint_data = {
            "session_id": session.id,
            "event_name": session.event.name,
            "page_group_name": pg.name,
            "pages": []
        }
        
        pgps = pg.pagegrouppage_set.all().order_by('order')
        for pgp in pgps:
            page = pgp.page
            
            page_scope = getattr(page, 'scope', 'ALL') or 'ALL'
            
            if scope == 'ADMIN' and page_scope != 'ADMIN':
                continue
            
            if scope == 'SUBJECT' and page_scope == 'ADMIN':
                continue

            page_data = {"id": page.id, "name": page.name, "components": []}
            
            pcs = page.pagecomponent_set.all().order_by('order')
            for pc in pcs:
                comp = pc.component
                page_data["components"].append({
                    "id": comp.id,
                    "type": comp.component_type.identifier,
                    "parameters": comp.parameter
                })
            blueprint_data["pages"].append(page_data)
            
        return Response(blueprint_data)

    @action(detail=True, methods=['post', 'put'])
    def save_metadata(self, request, pk=None):
        session = self.get_object()
        group_id = request.data.get('group_id')
        values = request.data.get('values', [])
        
        group = MetaDataGroup.objects.get(id=group_id)
        session_ct = ContentType.objects.get_for_model(Session)
        
        instance, created = MetaDataGroupInstance.objects.get_or_create(
            group=group,
            content_type=session_ct,
            object_id=session.id
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
    def saved_metadata(self, request, pk=None):
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        instances = MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        )
        
        saved_data = {}
        for inst in instances:
            for val in inst.values.all():
                saved_data[val.definition.id] = val.value
                
        return Response(saved_data)
        
    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        ).delete()
        
        import django.utils.timezone
        session.start_datetime = django.utils.timezone.now()
        session.save()
        
        return Response({"status": "session_reset"})

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        instances = MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        ).order_by('created_at')
        
        report_data = []
        for inst in instances:
            group_data = {
                "group_name": inst.group.name,
                "timestamp": inst.created_at,
                "answers": []
            }
            for val in inst.values.all().order_by('definition__name'):
                group_data["answers"].append({
                    "question": val.definition.name,
                    "answer": val.value,
                    "type": val.definition.expected_data_type
                })
            report_data.append(group_data)
            
        return Response({
            "session_id": session.id,
            "event_name": session.event.name,
            "page_group_name": session.page_group.name,
            "subject_identifier": session.subject.identifier,
            "start_time": session.start_datetime,
            "metadata_groups": report_data
        })