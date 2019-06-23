from pyramid.view import view_config
from kh_reminder.models import Reminder
from kh_reminder.lib.dbsession import Session


@view_config(route_name='reminders', renderer='json', permission='edit')
def reminders(request):
    reminders_data = []

    for reminder in Session.DBSession.query(Reminder).all():
        data = dict(id=reminder.id, item_string=reminder.item_string)
        reminders_data.append(data)

    return reminders_data
