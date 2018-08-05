from time import sleep
from datetime import datetime
from kh_reminder import nexmo_client, nexmo_number
from kh_reminder.models import DBSession, Attendant


def send_email(attendant, body):
    print(f'sending email to {attendant.fname} {attendant.lname}')


def send_text(attendant, text):
    print(f'sending sms to {attendant.fname} {attendant.lname}')
    to = "1" + str.join('', [num for num in attendant.phone if num.isdigit()])

    if len(to) != 11:
        print(f'Could not send sms to {attendant.fname} {attendant.lname} - invalid phone number')
        return

    sleep(1.1)
    status = nexmo_client.send_message({
        'from': nexmo_number,
        'to': to,
        'text': text
    })

    print(status)


def send_reminders():
    now = datetime.now()
    today = datetime(year=now.year, month=now.month, day=now.day)
    table_row = None
    old_rows = []

    for tbl_row in Schedule.table_rows:
        if (tbl_row.date - today).days == 1:
            table_row = tbl_row
            break

        elif (now - tbl_row.date).days > 7:
            old_rows.append(tbl_row)

    for tbl_row in old_rows:
        Schedule.table_rows.remove(tbl_row)

    if table_row is not None:
        for assignment in table_row.assignments:
            date_text = table_row.date_text
            task_text = assignment.task_text
            attendant_text = assignment.attendant_text

            for user in assignment.attendants:
                if len(user.split()) > 1:
                    fname, lname = user.split()[0:2]
                    if len(user.split()) == 3:
                        suffix = user.split()[2]
                        lname += ' ' + suffix
                else:
                    print(f'invalid name {user}, skipping')
                    continue

                attendant = DBSession.query(Attendant
                                            ).filter(Attendant.fname == fname
                                                     ).filter(Attendant.lname == lname).first()

                if attendant is not None:
                    msg = f'Kingdom Hall Reminder\n\n{date_text}\n\n{task_text}\n\n{attendant_text}'

                    if attendant.send_email == 1:
                        send_email(attendant, msg)

                    if attendant.send_sms == 1:
                        send_text(attendant, msg)

                else:
                    print(f'did not match {fname} {lname}')
