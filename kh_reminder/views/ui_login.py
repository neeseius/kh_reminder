from pyramid.security import remember, forget, authenticated_userid
from pyramid.view import forbidden_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from kh_reminder import auth_lock
from kh_reminder.lib import scheduler
from kh_reminder.lib.dbsession import Session
from kh_reminder.lib.notifications import Notify
from kh_reminder.models import Reminder
from time import sleep

@view_config(route_name='login', renderer='../templates/ui_login.jinja2')
@forbidden_view_config(renderer='../templates/ui_login.jinja2')
def login(request):
    referrer = request.path_info
    came_from = request.params.get('came_from', referrer)
    result = ''

    if request.params.get('action') == 'logout':
        headers = forget(request)
        return HTTPFound(location=request.route_url('login'), headers=headers)

    if request.params.get('action') == 'login':
        with auth_lock:
            if referrer == '/login':
                came_from = '/schedule'

            user_id = request.params.get('username')
            authenticated_userid(request)
            headers = remember(request, user_id)
            username = request.params.get('username')
            password = request.params.get('password')
            auth_pass, was_sealed = Session.authenticate(username, password)

            if auth_pass:
                if was_sealed:
                    for reminder in Session.DBSession.query(Reminder).all():
                        job = scheduler.add_job(Notify.send_reminders, args=[reminder.id], trigger='cron',
                            hour=reminder.hour,  minute=reminder.minute, id=str(reminder.id))
                    Session.DBSession.commit()
                return HTTPFound(location = came_from,
                                 headers = headers)
            else:
                result = 'Incorrect Username or Password'
                sleep(5)

    return dict(
        url=request.application_url + '/login',
        came_from=came_from,
        result=result
        )
