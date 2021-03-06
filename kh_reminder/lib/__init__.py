from datetime import datetime, timedelta
from .notifications import Notify
from apscheduler.schedulers.background import BackgroundScheduler


def date_from_element(date_el):
    """
    Converts the PDF Element that contains the meeting date and meeting type
    into a python date object and return that back
    """
    date_text = date_el.get_text().strip().split('\n')[0]
    month, day = date_text.split()
    now = datetime.now()
    duty_date = datetime.strptime('%s %s' % (month, day.zfill(2)), '%B %d')

    if (now.month - duty_date.month) > 8:
        return duty_date.replace(year=(now.year + 1))

    else:
        return duty_date.replace(year=now.year)


scheduler = BackgroundScheduler()
scheduler.add_job(Notify.send_reminders, trigger='cron', hour='19',  minute='0')
scheduler.start()
