from pyramid.view import view_config
from kh_reminder.models import Attendant, DBSession, collate
from kh_reminder.lib.reminder import send_reminders

@view_config(route_name='attendants', renderer='../templates/ui_attendants.jinja2', permission='edit')
def attendants(request):
    attendants = DBSession.query(Attendant).order_by(collate(Attendant.lname, 'NOCASE'))
    return {'attendants': attendants, 'path': request.path_info}
