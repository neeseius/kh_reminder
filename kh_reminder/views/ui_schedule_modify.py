from pyramid.view import view_config
from kh_reminder.models import Meeting, DBSession, Assignment


@view_config(route_name='schedule_modify', renderer='../templates/ui_schedule_modify.jinja2', permission='edit')
def schedule_modify(request):
    if 'name' in request.params:
        assignment_id = request.params.get('assignment_id')
        assignment = DBSession.query(Assignment).filter(Assignment.id == assignment_id).one()
        assignment.attendant = request.params.get("name")
        DBSession.commit()

    meeting_id = int(request.params.get('meeting_id'))
    meeting = DBSession.query(Meeting).filter(Meeting.id == meeting_id).one()

    return {'meeting': meeting,
            'path': request.path_info}
