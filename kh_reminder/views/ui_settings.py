from pyramid.view import view_config
from kh_reminder.models import Administrator
from kh_reminder.lib.dbsession import Session
import re


@view_config(route_name='settings', renderer='../templates/ui_settings.jinja2', permission='edit')
def settings(request):
    error = None
    changed = False

    username_object = Session.DBSession.query(Administrator).one()
    username = username_object.username

    if request.POST:
        new_username = request.params.get("username")
        new_password1 = request.params.get("password1")
        new_password2 = request.params.get("password2")

        if re.match("\w+", new_username).group(0) != new_username:
            error = "invalid username"

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                error = "passwords do not match"

            elif len(new_password1) < 10:
                error = "password must be 10 or more characters"

        if not error and username != new_username:
            username_object.username = new_username
            Session.DBSession.commit()
            username = new_username
            changed = True

        if not error and new_password1 and new_password2:
            Session.rekey_db(new_username, new_password1)
            changed = True

    return {'username': username,
            'error': error,
            'changed': changed,
            'path': request.path_info}
