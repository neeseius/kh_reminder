from datetime import datetime, timedelta
from kh_reminder.models import Meeting
from .datefromelement import date_from_element
from .pdfparser import PdfParser
from .meeting import CreateMeeting
from .dbsession import Session

class Schedule:
    @classmethod
    def generate_schedule(cls, pdf_document):
        """
        Given a PDF this function will generate a schedule from it.
        """
        date_elements, header_elements, elements = PdfParser.parse(pdf_document)
        cutoff_date = (datetime.now() - timedelta(days=10))

        for date_el in date_elements:
            date = date_from_element(date_el)

            if date > cutoff_date:
                CreateMeeting.create_meeting(date_el, header_elements, elements)

        Session.DBSession.commit()

    @staticmethod
    def cleanup_schedule():
        """
        Cleanup old meetings from the database.
        """
        cutoff_date = (datetime.now() - timedelta(days=10))

        for meeting in Session.DBSession.query(Meeting).filter(Meeting.date < cutoff_date).all():
            for assignment in meeting.assignments:
                Session.DBSession.delete(assignment)

            Session.DBSession.delete(meeting)

    @classmethod
    def flush_schedule(cls):
        for meeting in Session.DBSession.query(Meeting).all():
            for assignment in meeting.assignments:
                Session.DBSession.delete(assignment)

            Session.DBSession.delete(meeting)

        Session.DBSession.commit()
