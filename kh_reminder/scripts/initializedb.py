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
    settings = get_appsettings('../development.ini')
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    main()
