from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
#from kh_reminder.models import Base, DBSession, RootFactory
from kh_reminder.models import RootFactory, engine, define_engine
from threading import Lock
import nexmo


def acl(user, request):
    if user:
        return ['group:edit']


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    global nexmo_client, nexmo_number, auth_lock
    Settings = settings

    auth_lock = Lock()

    nexmo_number = settings['nexmo.number']
    nexmo_client = nexmo.Client(key=settings['nexmo.key'],
                 secret=settings['nexmo.secret'])

    engine["engine"] = engine_from_config(settings, 'sqlalchemy.')

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
    config.add_route('attendants', '/attendants')
    config.add_route('attendant_modify', '/attendant/modify')

    config.scan()

    return config.make_wsgi_app()

