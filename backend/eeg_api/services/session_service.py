import os
from typing import Dict, Any

from django.contrib.contenttypes.models import ContentType
from eeg_api.models import (
    Session, MetaDataGroupInstance, EEGDataFile, 
    HeartRateDataFile, GenericRecording, EventSubjectAssignment
)


def generate_blueprint(session: Session, scope: str = 'ALL') -> Dict[str, Any]:
    """Generates the UI blueprint dictionary based on the requested user scope."""
    pg = session.page_group
    event_group_id = None
    
    if session.subject and session.event:
        assignment = EventSubjectAssignment.objects.filter(
            subject=session.subject, 
            event=session.event
        ).first()
        
        if assignment and assignment.group:
            event_group_id = assignment.group.id
            
    blueprint_data = {
        "session_id": session.id,
        "event_name": session.event.name,
        "page_group_name": pg.name,
        "page_group_id": pg.id,
        "event_id": session.event.id,
        "event_group_id": event_group_id,
        "event_logo": session.event.logo.file.url if getattr(session.event, 'logo', None) and session.event.logo.file else None,
        "pages": []
    }
    
    pgps = pg.pagegrouppage_set.all().order_by('order')
    for pgp in pgps:
        page = pgp.page
        page_scope = getattr(page, 'scope', 'ALL') or 'ALL'
        
        # Enforce scope permissions
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
        
    return blueprint_data


def generate_report(session: Session) -> Dict[str, Any]:
    """Compiles all metadata answers and recorded files into a comprehensive session report."""
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

    files_list = []

    def get_filename(file_field) -> str:
        """Extracts the base filename safely."""
        if file_field and file_field.name:
            return os.path.basename(file_field.name)
        return "Unbenannt"

    # Collect all associated files
    for eeg in EEGDataFile.objects.filter(session=session):
        files_list.append({
            "type": "EEG", "category": "", "order": eeg.order,
            "name": get_filename(eeg.file), "description": eeg.description,
            "url": eeg.file.url if eeg.file else None
        })

    for hr in HeartRateDataFile.objects.filter(session=session):
        files_list.append({
            "type": "Heart Rate", "category": "", "order": hr.order,
            "name": get_filename(hr.file), "description": hr.description,
            "url": hr.file.url if hr.file else None
        })

    for gen in GenericRecording.objects.filter(session=session).select_related('category'):
        files_list.append({
            "type": "Generic", "category": gen.category.name if gen.category else "",
            "order": gen.order, "name": get_filename(gen.file),
            "description": gen.description, "url": gen.file.url if gen.file else None
        })

    sorted_files = sorted(files_list, key=lambda x: x['order'] if x['order'] is not None else 999)
        
    return {
        "session_id": session.id,
        "event_name": session.event.name if session.event else None,
        "page_group_name": session.page_group.name if session.page_group else None,
        "subject_identifier": session.subject.identifier if session.subject else None,
        "start_time": session.start_datetime,
        "location_name": session.location.name if session.location else None,
        "metadata_groups": report_data,
        "uploaded_files": sorted_files
    }