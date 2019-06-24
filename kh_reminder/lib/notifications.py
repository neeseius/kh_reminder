from kh_reminder.models import Attendant, Meeting, Signature, Reminder
from kh_reminder.lib.dbsession import Session, Administrator
from threading import Lock
from time import sleep
from datetime import datetime, timedelta
import nexmo
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sms_notification_lock = Lock()
email_notification_lock = Lock()


class Notify:
    nexmo_number = None
    nexmo_client = None

    @classmethod
    def initialize_nexmo_client(cls, settings):
        cls.nexmo_number = settings['nexmo.number']
        cls.nexmo_client = nexmo.Client(key=settings['nexmo.key'],
                                        secret=settings['nexmo.secret'])

    @staticmethod
    def send_test_email(admin):
        email_session = Notify.get_email_session(admin)
        message = MIMEMultipart()
        message['From'] = admin.email
        message['To'] = admin.email
        message['Subject'] = 'kh_reminder test'
        message.attach(MIMEText("Test Email from kh_reminder", 'plain'))
        email_session.sendmail(admin.email, admin.email, message.as_string())


    @staticmethod
    def get_email_session(admin):
        email_session = smtplib.SMTP(admin.email_smtp, 587)
        email_session.ehlo()
        email_session.starttls()
        email_session.login(admin.email, admin.email_password)
        return email_session

    @staticmethod
    def send_email(attendant, body, admin_email, email_session):
        message = MIMEMultipart()
        message['From'] = admin_email
        message['To'] = attendant.email
        message['Subject'] = 'Assignment Reminder'
        message.attach(MIMEText(body, 'plain'))
        email_session.sendmail(admin_email, attendant.email, message.as_string())

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
        admin = Session.DBSession.query(Administrator).one()
        email_session = None
        reminder = None
        now = datetime.now()
        today = datetime(year=now.year, month=now.month, day=now.day)
        successfully_sent = 0
        not_sent = 0

        # Check that admin has properly set up email in settings
        if admin.can_email == 1:
            try:
                email_session = cls.get_email_session(admin)
            except Exception as e:
                print(e)
                print("Couldn't established email session, skipping emails")

        # Meeting is only set if ad-hoc alerts are sent from the web portal
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

            # Insure attendant has notifications of some kind enabled
            if (attendant is not None) and (attendant.send_email == 1 or attendant.send_sms == 1):

                msg = (f'Kingdom Hall Reminder\n\n'
                       f'Date: {meeting.date.strftime("%A %B %d")} {meeting.meeting_type}\n'
                       f'Assignment: {assignment.assignment_type}\n'
                       f'Assignee: {attendant.fullname}')

                signature = Session.DBSession.query(Signature).one()
                if signature.message != "":
                    msg += f"\n\n\n{signature.message}"

                # Send email notification
                if (attendant.send_email == 1) and (not reminder or "email" in reminder.msg_type):
                    print(f'sending email notification for {assignment.assignment_type} on {meeting.date}')
                    with email_notification_lock:
                        try:
                            cls.send_email(attendant=attendant, body=msg, admin_email=admin.email, email_session=email_session)
                            sent = True
                        except Exception as e:
                            sent = False

                # Send sms notification
                if (attendant.send_sms == 1) and email_session and (not reminder or "text" in reminder.msg_type):
                    print(f'sending text notification for {assignment.assignment_type} on {meeting.date}')
                    with sms_notification_lock:
                        try:
                            cls.send_text(attendant=attendant, text=msg)
                            sent = True
                        except Exception as e:
                            sent = False

                if sent:
                    successfully_sent += 1
                else:
                    not_sent +=1

            else:
                not_sent += 1

        if email_session:
            email_session.quit()

        # Let admin know result
        if admin.phone:
            msg = ( f'kh_reminder Summary'
                    f'Date: {meeting.date.strftime("%A %B %d")} {meeting.meeting_type}\n')
            if reminder:
                msg += reminder.item_string + "\n"
            msg += f"\nsuccessfully sent: {successfully_sent}\nnot sent: {not_sent}"
            cls.send_text(number=admin.phone, text=msg)

        else:
            print(f'No alert sent for {assignment.assignment_type} on {meeting.date}')

