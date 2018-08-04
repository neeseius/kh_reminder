from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal
from kh_reminder import models
from datetime import datetime, timedelta

rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)


def get_date_from_el(date_el):
    date_text = date_el.get_text().strip().split('\n')[0]
    month, day = date_text.split()
    now = datetime.now()
    duty_date = datetime.strptime('%s %s' % (month, day.zfill(2)), '%B %d')
    if (now.month - duty_date.month) > 8:
        return duty_date.replace(year=(now.year + 1))
    else:
        return duty_date.replace(year=now.year)


class Meeting:
    @classmethod
    def create_meeting(cls, date_el, header_elements, elements):
        date_text = date_el.get_text().strip()
        date = get_date_from_el(date_el)
        assignments, assignment_types = cls._get_assignments(date, date_el, header_elements, elements)
        cls._generate_meeting(date, date_text, assignments, assignment_types)

    def _get_assignments(date, date_el, header_elements, elements):
        assignments = []
        assignment_types = []
        for header_el in header_elements:
            assignment_type = header_el.get_text().strip().replace('\n', ' ')
            assignment_types.append(assignment_type)
            assignments += Assignment.create_assignments(
                    date_el, header_el, elements, assignment_type)
        return assignments, assignment_types

    def _generate_meeting(date, date_text, assignments, assignment_types):
        meeting_type = date_text.split('\n')[1]
        meeting = models.Meeting(
                date = date,
                meeting_type = meeting_type,
                assignment_types = str.join(',', assignment_types))
        meeting.assignments += assignments

        conflict_meeting = models.DBSession.query(models.Meeting)\
            .filter(models.Meeting.date == date.strftime('%F')).first()

        if conflict_meeting:
            for assignment in conflict_meeting.assignments:
                models.DBSession.delete(assignment)
            models.DBSession.delete(conflict_meeting)

        models.DBSession.add(meeting)


class Assignment:
    @classmethod
    def create_assignments(cls, date_el, header_el, elements, assignment_type):
        attendants = cls._get_attendants(date_el, header_el, elements)
        assignments = cls._get_assignments(assignment_type, attendants)
        return assignments

    def _get_attendants(date_el, header_el, elements):
        attendants = []
        for el in elements:
            if header_el.is_hoverlap(el) and date_el.is_voverlap(el):
                attendant_el = el
                attendant_text = el.get_text().replace('2', '').strip()
                attendants = [attendant.replace('-', '').strip() for attendant in attendant_text.split('\n')]
                return attendants

    def _get_assignments(assignment_type, attendants):
        assignments = []
        for attendant in attendants:
            assignment = models.Assignment(assignment_type, attendant)
            assignments.append(assignment)
        return assignments


class PdfParser:
    @classmethod
    def parse(cls, document):
        elements = cls._get_elements(document)
        header_elements = cls._get_header_elements(elements)
        cls.table_headers = [el.get_text().strip() for el in header_elements]
        date_elements = cls._get_date_elements(elements)
        cls._generate_schedule(date_elements, header_elements, elements)

    @staticmethod
    def _get_elements(doc):
        elements = []
        for page in PDFPage.get_pages(doc):
            interpreter.process_page(page)
            layout = device.get_result()
            for el in layout:
                if isinstance(el, LTTextBoxHorizontal):
                    elements.append(el)
        return elements

    @staticmethod
    def _get_date_elements(elements):
        date_elements = []
        for el in elements:
            if 'Meeting' in el.get_text():
                date_elements.append(el)
        date_elements = sorted(date_elements, key=lambda e: e.y0, reverse=True)
        return date_elements

    @staticmethod
    def _get_header_elements(elements):
        reference_element = None
        header_elements = []
        for el in elements:
            if 'Microphones' in el.get_text():
                reference_element = el
                break
        for el in elements:
            if reference_element.is_voverlap(el):
                header_elements.append(el)
        header_elements = sorted(header_elements, key=lambda e: e.x0)
        return header_elements

    def _cleanup_schedule():
        cutoff_date = (datetime.now() - timedelta(days=10))
        for meeting in models.DBSession.query(models.Meeting).filter(models.Meeting.date < cutoff_date).all():
            for assignment in meeting.assignments:
                models.DBSession.delete(assignment)
            models.DBSession.delete(meeting)


    @classmethod
    def _generate_schedule(cls, date_elements, header_elements, elements):
        cutoff_date = (datetime.now() - timedelta(days=10))
        for date_el in date_elements:
            date = get_date_from_el(date_el)
            if (date > cutoff_date):
                Meeting.create_meeting(date_el, header_elements, elements)

        cls._cleanup_schedule()
        models.DBSession.commit()


    @classmethod
    def flush(cls):
        pass
