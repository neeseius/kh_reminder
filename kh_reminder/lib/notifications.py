from kh_reminder.models import Attendant, Meeting
from kh_reminder.lib.dbsession import Session
from time import sleep
from datetime import datetime, timedelta
import nexmo


class Notify:
    nexmo_number = None
    nexmo_client = None

    @classmethod
    def initialize_nexmo_client(cls, settings):
        cls.nexmo_number = settings['nexmo.number']
        cls.nexmo_client = nexmo.Client(key=settings['nexmo.key'],
                                        secret=settings['nexmo.secret'])

    @staticmethod
    def send_email(attendant, body):
        pass

    @classmethod
    def send_text(cls, text, number=None, attendant=None):
        if attendant:
            to = "1" + str.join('', [num for num in attendant.phone if num.isdigit()])

        else:
            to = "1" + number

        status = cls.nexmo_client.send_message({
            'from': cls.nexmo_number,
            'to': to,
            'text': text
        })

        sleep(1.1)

        return status


    @classmethod
    def send_reminders(cls, meeting=None):
        if Session.status == "sealed":
            print("Database is sealed, skipping alerts")
            return

        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        tomorrow = (today + timedelta(days=1))

        if not meeting:
            meeting = Session.DBSession.query(Meeting).filter(Meeting.date == tomorrow.strftime("%F")).first()
            if not meeting:
                print("No meeting found for tomorrow, skipping alerts")
                return

        for assignment in meeting.assignments:
            if "assembly" in assignment.attendant.lower() or "convention" in assignment.attendant.lower():
                continue

            attendant = Session.DBSession.query(Attendant).filter(Attendant.fullname == assignment.attendant).first()

            if (attendant is not None) and (attendant.send_email == 1 or attendant.send_sms == 1):
                msg = (f'Kingdom Hall Reminder\n\n'
                       f'Date: {meeting.date.strftime("%A %B %d")} {meeting.meeting_type}\n'
                       f'Assignment: {assignment.assignment_type}\n'
                       f'Assignee: {attendant.fullname}')

                if attendant.send_email == 1:
                    cls.send_email(attendant, msg)

                if attendant.send_sms == 1:
                    print(f'sending sms notification for {assignment.assignment_type} on {meeting.date}')
                    cls.send_text(attendant=attendant, text=msg)

            else:
                print(f'No alert sent for {assignment.assignment_type} on {meeting.date}')