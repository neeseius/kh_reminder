from kh_reminder.models import Attendant, Meeting, Signature, Reminder
from kh_reminder.lib.dbsession import Session
from threading import Lock
from time import sleep
from datetime import datetime, timedelta
import nexmo

notification_lock = Lock()


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
    def send_reminders(cls, reminder_id=None, meeting=None):
        reminder = None
        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        target_date = None

        if not meeting:
            reminder = Session.DBSession.query(Reminder).filter(Reminder.id == reminder_id).one()
            target_date = (today + timedelta(days=reminder.days_delta))
            if reminder.meeting == "Any":
                meeting = Session.DBSession.query(Meeting).filter(Meeting.date == target_date.strftime("%F")).first()
            else:
                meeting = Session.DBSession.query(Meeting)\
                    .filter(Meeting.date == target_date.strftime("%F"))\
                    .filter(Meeting.meeting_type == reminder.meeting).first()
            if not meeting:
                print(f"no meeting found for reminder: {reminder.item_string}")
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

                signature = Session.DBSession.query(Signature).one()
                if signature.message != "":
                    msg += f"\n\n\n{signature.message}"

                if (attendant.send_email == 1) and (not reminder or "email" in reminder.msg_type):
                    print(f'sending email notification for {assignment.assignment_type} on {meeting.date}')
                    with notification_lock:
                        cls.send_email(attendant=attendant, body=msg)

                if (attendant.send_sms == 1) and (not reminder or "text" in reminder.msg_type):
                    print(f'sending text notification for {assignment.assignment_type} on {meeting.date}')
                    with notification_lock:
                        cls.send_text(attendant=attendant, text=msg)

            else:
                print(f'No alert sent for {assignment.assignment_type} on {meeting.date}')
