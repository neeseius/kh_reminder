from .reminder import send_reminders
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, trigger='cron', hour='19',  minute='0')
scheduler.start()
