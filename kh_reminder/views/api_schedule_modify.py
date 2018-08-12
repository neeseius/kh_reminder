from pyramid.view import view_config
from kh_reminder.models import Meeting, Assignment
from kh_reminder.lib.dbsession import Session


@view_config(route_name='schedule_modify_api', renderer='json', permission='edit')
def schedule_modify_api(request):
    # Assignee is being modified
    data = request.json_body
    assignment_id = data['assignment_id']

    assignment = Session.DBSession.query(Assignment).filter(Assignment.id == assignment_id).one()
    assignment.attendant = data['name']
    Session.DBSession.commit()

    return {"status": "attendant changed"}
