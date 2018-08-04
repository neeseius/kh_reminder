import os
import sys
import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings
from kh_reminder.models import (
    DBSession,
    Base,
    Attendant
    )


def main():
    thisdir = os.path.dirname(os.path.abspath(__file__))
    ini = os.path.join(thisdir, os.path.pardir, os.path.pardir, 'development.ini')
    settings = get_appsettings(ini)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    main()
