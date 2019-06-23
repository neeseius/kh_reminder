from pyramid.view import view_config
from pyramid.response import Response
from kh_reminder.models import Reminder
from kh_reminder.lib.dbsession import Session
from kh_reminder.lib import scheduler


@view_config(route_name='reminders_del', renderer='json', permission='edit')
def reminders_del(request):
    _id = int(request.params.get("id"))
    reminder = Session.DBSession.query(Reminder).filter(Reminder.id == _id).one()
    scheduler.remove_job(str(reminder.id))
    Session.DBSession.delete(reminder)
    Session.DBSession.commit()
    
    return Response(status=204)
