from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal
from datetime import datetime
import pickle
import os

rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
thisdir = os.path.dirname(os.path.abspath(__file__))


def get_date_from_el(date_el):
    date_text = date_el.get_text().strip().split('\n')[0]
    month, day = date_text.split()
    now = datetime.now()
    duty_date = datetime.strptime('%s %s' % (month, day.zfill(2)), '%B %d')
    if (now.month - duty_date.month) > 8:
        return duty_date.replace(year=(now.year + 1))
    else:
        return duty_date.replace(year=now.year)


class TableRow:
    def __init__(self, date_el, header_elements, elements):
        self.date_el = date_el
        self.date_text = date_el.get_text().strip()
        self.date = get_date_from_el(date_el)
        self.assignments = []
        self._get_assignments(header_elements, elements)

    def _get_assignments(self, header_elements, elements):
        for header_el in header_elements:
            asgmt = Assignment(self.date_el, self.date, header_el, elements)
            self.assignments.append(asgmt)


class Assignment:
    def __init__(self, date_el, date, header_el, elements):
        self.date_el = date_el
        self.date = date
        self.header_el = header_el
        self.task_text = header_el.get_text().strip()
        self.attendant_el = None
        self.attendant_text = None
        self.attendants = []
        self.attendants_in_db = True
        self._get_attendant(elements)

    def _get_attendant(self, elements):
        for el in elements:
            if self.header_el.is_hoverlap(el) and self.date_el.is_voverlap(el):
                self.attendant_el = el
                self.attendant_text = el.get_text().replace('2', '').strip()
                self.attendants = self.attendant_text.replace('-', '').strip().split('\n')
                break


class Schedule:
    table_headers = []
    table_rows = []

    @classmethod
    def parse(cls, document):
        elements = cls._get_elements(document)
        header_elements = cls._get_header_elements(elements)
        cls.table_headers = [el.get_text().strip() for el in header_elements]
        date_elements = cls._get_date_elements(elements)
        cls._generate_schedule(date_elements, header_elements, elements)
        with open(os.path.join(thisdir, '../.appdata'), 'wb') as appdata:
            data = (cls.table_headers, cls.table_rows)
            pickle.dump(data, appdata)

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

    @classmethod
    def _generate_schedule(cls, date_elements, header_elements, elements):
        new_table_rows = []
        for date_el in date_elements:
            now = datetime.now()
            date = get_date_from_el(date_el)
            query = filter(lambda row: row.date.strftime('%F') == date.strftime('%F'), cls.table_rows)
            if len([*query]) == 0 and (now - date).days < 8:
                table_row = TableRow(date_el, header_elements, elements)
                new_table_rows.append(table_row)
        cls.table_rows += new_table_rows

    @classmethod
    def flush(cls):
        cls.table_headers = []
        cls.table_rows = []
        if os.path.exists(os.path.join(thisdir, '../.appdata')):
            os.remove(os.path.join(thisdir, '../.appdata'))

if os.path.exists(os.path.join(thisdir, '../.appdata')):
    with open(os.path.join(thisdir, '../.appdata'), 'rb') as appdata:
        table_headers, table_rows = pickle.load(appdata)
        Schedule.table_headers = table_headers
        Schedule.table_rows = table_rows
