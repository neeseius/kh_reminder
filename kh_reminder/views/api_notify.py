from pyramid.view import view_config
from kh_reminder.lib.notifications import Notify
from kh_reminder.lib.dbsession import Session
from kh_reminder.models import Administrator, Meeting


@view_config(route_name='notify', renderer='json', permission='edit')
def notify(request):
    data = request.json_body

    if "phone" in data:
        phone = data["phone"]
        phone = str.join('', [num for num in phone if num.isalnum])

        if len(phone) != 10:
            return {"status": "invalid phone number"}

        admin = Session.DBSession.query(Administrator).one().username
        message = f"kh_reminder\n{admin} is sending you a test notification"
        status = Notify.send_text(text=message, number=phone)

        if status["messages"][0]["status"] == "0":
            return {"status": "sms sent"}

        else:
            return {"status": "ERROR"}

    elif "meeting_id" in data:
        meeting_id = data["meeting_id"]
        meeting = Session.DBSession.query(Meeting).filter(Meeting.id == meeting_id).one()
        Notify.send_reminders(meeting)

        return {"status": "reminders sent"}