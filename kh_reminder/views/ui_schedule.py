from pyramid.view import view_config
from kh_reminder.lib.schedule import Schedule
from datetime import datetime, timedelta, date
from kh_reminder.models import Attendant, Meeting
from kh_reminder.lib.dbsession import Session


@view_config(route_name='schedule', renderer='../templates/ui_schedule.jinja2', permission='edit')
def schedule(request):
    # The user uploaded a PDF
    if 'pdf' in request.params:
        pdf_file = request.params.get('pdf')
        if hasattr(pdf_file, "file"):
            pdf_document = pdf_file.file
            Schedule.generate_schedule(pdf_document)
            Schedule.cleanup_schedule()

    # The user is deleting the schedule
    elif 'flush' in request.params:
        Schedule.flush_schedule()

    # Do not display meeting older than n days
    before_date = (datetime.now() - timedelta(days=10))
    attendants = {}

    # Discover attendants that are in the database
    for attendant in Session.DBSession.query(Attendant).all():
        attendants[attendant.fullname] = attendant.id

    meetings = Session.DBSession.query(Meeting).filter(Meeting.date > before_date).order_by(Meeting.date).all()

    # Mark which meeting date is next
    today = datetime.now()
    next_date = None
    for meeting in meetings:
        meeting_date = datetime(meeting.date.year, meeting.date.month, meeting.date.day, 00, 00)
        if meeting_date > today or meeting.date.strftime("%F") == today.strftime("%F"):
            next_date = meeting.date
            break

    # Discover assignment types for the headers
    assignment_types = []
    if meetings:
        assignment_types = []
        for assignment in meetings[0].assignment_types.split(','):
            assignment_types.append(assignment)

    return {'assignment_types': assignment_types,
            'next_date': next_date,
            'meetings': meetings,
            'attendants': attendants,
            'path': request.path_info}
