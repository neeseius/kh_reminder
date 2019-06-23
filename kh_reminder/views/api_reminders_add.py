from pyramid.view import view_config
from pyramid.response import Response
from kh_reminder.models import Reminder
from kh_reminder.lib.dbsession import Session
from kh_reminder.lib.notifications import Notify
from kh_reminder.lib import scheduler


@view_config(route_name='reminders_add', renderer='json', permission='edit')
def reminders_add(request):
    hour, minute = request.json_body.get("at").split(":")
    reminder = Reminder(
        hour = int(hour),
        minute = int(minute),
        meeting = request.json_body.get("meeting"),
        msg_type = request.json_body.get("msg_type"),
        days_delta = request.json_body.get("days")
    )

    if Session.DBSession.query(Reminder).filter(Reminder.item_string == reminder.item_string).first():
        return Response(status=204)

    Session.DBSession.add(reminder)
    Session.DBSession.commit()

    job = scheduler.add_job(Notify.send_reminders, args=[reminder.id], trigger='cron', hour=hour, minute=minute, id=str(reminder.id))

    return {'id': reminder.id, 'item_string': reminder.item_string}
