from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal

rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)


class PdfParser:
    """
    Retrieve the PDF element objects from the given PDF and
    return them for use by other functions via parse.
    """

    @classmethod
    def parse(cls, pdf_document):
        elements = cls._get_elements(pdf_document)
        header_elements = cls._get_header_elements(elements)
        #table_headers = [el.get_text().strip() for el in header_elements]
        date_elements = cls._get_date_elements(elements)
        return date_elements, header_elements, elements

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
