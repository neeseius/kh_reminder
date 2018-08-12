from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from kh_reminder.models import RootFactory
from kh_reminder.lib.dbsession import Session
from threading import Lock
from kh_reminder.lib.notifications import Notify

auth_lock = Lock()

def acl(user, request):
    if user:
        return ['group:edit']


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    Notify.initialize_nexmo_client(settings)

    engine = engine_from_config(settings, 'sqlalchemy.')
    Session.engine_object = engine

    authn_policy = AuthTktAuthenticationPolicy(settings['authn.key'], callback=acl, hashalg='sha512',
                                               timeout=900, reissue_time=450)

    config = Configurator(settings=settings, root_factory=RootFactory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.include('pyramid_jinja2')

    config.add_static_view(name='static', path='static')
    config.add_route('login', '/login')
    config.add_route('schedule', '/schedule')
    config.add_route('schedule_modify', '/schedule/modify')
    config.add_route('schedule_modify_api', '/schedule/modify_api')
    config.add_route('attendants', '/attendants')
    config.add_route('attendant_modify', '/attendant/modify')
    config.add_route('notify_api', '/notify_api')
    config.add_route('settings', '/settings')

    config.scan()

    return config.make_wsgi_app()

