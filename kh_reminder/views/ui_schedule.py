from pyramid.view import view_config
from kh_reminder.lib.schedule import PdfParser
from datetime import datetime, timedelta
from kh_reminder.models import Attendant, Meeting, DBSession

@view_config(route_name='schedule', renderer='../templates/ui_schedule.jinja2', permission='edit')
def schedule(request):
    if request.POST:
        document = request.params.get('pdf').file
        PdfParser.parse(document)
    elif 'flush' in request.params:
        PdfParser.flush()

    #now = datetime.now()
    #today = datetime(year=now.year, month=now.month, day=now.day)
    next_date = None

    #for table_row in Schedule.table_rows:
    #    if (table_row.date - today).days >= 0:
    #        next_date = table_row.date
    #        break

    before_date = (datetime.now() - timedelta(days=10))
    attendants = [f'{attendant.fname} {attendant.lname}' for attendant in DBSession.query(Attendant).all()]
    meetings = DBSession.query(Meeting).filter(Meeting.date > before_date).all()
    assignment_types = []
    if meetings:
        assignment_types = [assignment for assignment in meetings[0].assignment_types.split(',')]

    return {#'schedule': Schedule,
            'assignment_types': assignment_types,
            'next_date': next_date,
            'meetings': meetings,
            'attendants_in_db': attendants,
            'path': request.path_info}
