from kh_reminder.models import Meeting, Assignment
from .dbsession import Session
from . import date_from_element


class CreateMeeting:
    @classmethod
    def create_meeting(cls, date_element, header_elements, elements):
        """
        Create a meeting by dissecting pdf elements
        """
        date = date_from_element(date_element)
        assignments, assignment_types = cls._get_assignments(date_element, header_elements, elements)

        # Date of the meeting is the first line,
        # weekend or midweek meeting is the second line
        date_text = date_element.get_text().strip()
        meeting_type = date_text.split('\n')[1]

        meeting = Meeting(
            date=date,
            meeting_type=meeting_type,
            assignment_types=str.join(',', assignment_types))

        meeting.assignments += assignments

        conflict_meeting = Session.DBSession.query(Meeting) \
            .filter(Meeting.date == date.strftime('%F')).first()

        if conflict_meeting:
            for assignment in conflict_meeting.assignments:
                Session.DBSession.delete(assignment)

            Session.DBSession.delete(conflict_meeting)

        Session.DBSession.add(meeting)

    @classmethod
    def _get_assignments(cls, date_element, header_elements, elements):
        assignments = []
        assignment_types = []

        # Header element is the name of the assignment
        for header_el in header_elements:
            assignment_type_raw = header_el.get_text().strip()
            strip_chars = [2, "(", ")"]
            assignment_type = str.join('', [char for char in assignment_type_raw if char not in strip_chars]).strip()
            assignment_types.append(assignment_type)
            attendants = cls._get_attendants_for_assignment(date_element, header_el, elements)

            if '\n' in assignment_type:
                a_types = assignment_type.split('\n')
                for index, attendant in enumerate(attendants):
                    assignment = Assignment(a_types[index], attendant)
                    assignments.append(assignment)

            else:
                for attendant in attendants:
                    assignment = Assignment(assignment_type, attendant)
                    assignments.append(assignment)

        return assignments, assignment_types

    def _get_attendants_for_assignment(date_element, header_element, elements):
        # Find the elements that contain names
        for element in elements:

            # Intersection points on the schedule grid can be found via overlaps
            if header_element.is_hoverlap(element) and date_element.is_voverlap(element):
                text = element.get_text()
                strip_chars = [2, "(", ")"]
                attendant_text = str.join('', [char for char in text if char not in strip_chars]).strip()
                attendants = []

                # Some elements have multiple names in them
                for attendant in attendant_text.split('\n'):
                    attendants.append(attendant.replace('-', '').strip())

                return attendants
