from .notifications import Notify
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(Notify.send_reminders, trigger='cron', hour='19',  minute='0')
scheduler.start()
