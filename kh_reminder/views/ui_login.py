from pyramid.security import remember, forget, authenticated_userid, Allow
from pyramid.view import forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from kh_reminder import auth_lock
from kh_reminder.models import define_engine
from time import sleep

@view_config(route_name='login', renderer='../templates/ui_login.jinja2')
@forbidden_view_config(renderer='../templates/ui_login.jinja2')
def login(request):
    referrer = request.path_info
    came_from = request.params.get('came_from', referrer)
    result = ''
    if request.params.get('action') == 'logout':
        headers = forget(request)
        return HTTPFound(location = request.route_url('login'),
                 headers = headers)

    if request.params.get('action') == 'login':
        with auth_lock:
            if referrer == '/login':
                came_from = '/schedule'

            user_id = request.params.get('username')
            authenticated_userid(request)
            headers = remember(request, user_id)
            user = request.params.get('username')
            passwd = request.params.get('password')

            if define_engine(passwd):
                return HTTPFound(location = came_from,
                                 headers = headers)
            else:
                result = 'Incorrect Username or Password'
                sleep(.1)
        #with auth_lock:
        #    if referrer == '/login':
        #        came_from = '/schedule'
        #    user_id = request.params.get('username')
        #    authenticated_userid(request)
        #    headers = remember(request, user_id)
        #    user = request.params.get('username')
        #    passw = request.params.get('password')
        #    if user == admin_user and passw == admin_pass:
        #        return HTTPFound(location = came_from,
        #                         headers = headers)
        #    else:
        #        result = 'Incorrect Username or Password'
        #        sleep(5)

    return dict(
        url = request.application_url + '/login',
        came_from = came_from,
        result = result
        )
