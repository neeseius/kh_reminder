from pyramid.view import view_config
from sqlalchemy import collate
from kh_reminder.models import Attendant
from kh_reminder.lib.dbsession import Session

@view_config(route_name='attendants', renderer='../templates/ui_attendants.jinja2', permission='edit')
def attendants(request):
    attendants = Session.DBSession.query(Attendant).order_by(collate(Attendant.lname, 'NOCASE'))

    return {'attendants': attendants, 'path': request.path_info}
