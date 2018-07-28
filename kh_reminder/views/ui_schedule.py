from pyramid.view import view_config
from kh_reminder.lib.schedule import Schedule
from datetime import datetime
from kh_reminder.models import Attendant, DBSession

@view_config(route_name='schedule', renderer='../templates/ui_schedule.jinja2', permission='edit')
def schedule(request):
    if request.POST:
        document = request.params.get('pdf').file
        Schedule.parse(document)
    elif 'flush' in request.params:
        Schedule.flush()

    now = datetime.now()
    today = datetime(year=now.year, month=now.month, day=now.day)
    next_date = None
    for table_row in Schedule.table_rows:
        if (table_row.date - today).days >= 0:
            next_date = table_row.date
            break

    attendants_in_db = [f'{attendant.fname} {attendant.lname}' for attendant in DBSession.query(Attendant).all()]

    return {'schedule': Schedule,
            'next_date': next_date,
            'attendants_in_db': attendants_in_db,
            'path': request.path_info}
