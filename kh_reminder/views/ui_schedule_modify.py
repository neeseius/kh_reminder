from pyramid.view import view_config
from kh_reminder.models import Meeting, Assignment
from kh_reminder.lib.dbsession import Session


@view_config(route_name='schedule_modify', renderer='../templates/ui_schedule_modify.jinja2', permission='edit')
def schedule_modify(request):
    # Assignee is being modified
    if 'name' in request.params:
        assignment_id = request.params.get('assignment_id')
        assignment = Session.DBSession.query(Assignment).filter(Assignment.id == assignment_id).one()
        assignment.attendant = request.params.get("name")
        Session.DBSession.commit()

    next_meeting = request.params.get("next_meeting") == "true"
    meeting_id = int(request.params.get('meeting_id'))
    meeting = Session.DBSession.query(Meeting).filter(Meeting.id == meeting_id).one()

    return {'meeting': meeting,
            'next_meeting': next_meeting,
            'path': request.path_info}
