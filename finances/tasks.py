from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler import util
from django.core.mail import send_mass_mail
from django.conf import settings
from django.core import mail
from datetime import datetime

from .models import Tunnel, Notification
from .utils import download_stock_history, format_email_message

print('Creating scheduler...')
scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
print('Scheduler created!')
tunnel_id_set = set()
notification_set = set()

def schedule_jobs():
    scheduler.add_jobstore(DjangoJobStore(), "default")
    print("Scheduling database watcher")
    scheduler.add_job(
        __watch_database,
        trigger=CronTrigger(minute="*/1"),
        id='database_watcher',
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        __send_emails,
        trigger=CronTrigger(minute="*/1"),
        id='emails_sender',
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()

@util.close_old_connections
def __watch_database():
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Looking for new tunnels in database...')
    tunnels = Tunnel.objects.all()
    for tunnel in tunnels:
        if tunnel.id not in tunnel_id_set:
            __watch_tunnel(tunnel)

def __watch_tunnel(tunnel: Tunnel):
    tunnel_id_set.add(tunnel.id)
    scheduler.add_job(
        __check_tunnel,
        args=(tunnel,),
        trigger=CronTrigger(minute=f"*/{tunnel.time_interval}"),
        id=f'tunnel#{tunnel.id}',
        max_instances=1,
        replace_existing=True,
    )
    print(f'Schedule added for tunnel#{tunnel.id} ({tunnel.stock_symbol})')

@util.close_old_connections
def __check_tunnel(tunnel: Tunnel):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Running task for tunnel#{tunnel.id}')
    stock_symbol = tunnel.stock_symbol
    history = download_stock_history(stock_symbol)
    stock_datetime = history['datetime'].iloc[-1]
    stock_price = history['price'].iloc[-1]
    print(f'{stock_symbol} => {stock_price}')

    try:
        last_notification_dt = Notification.objects.filter(tunnel=tunnel).latest('datetime').datetime
    except Notification.DoesNotExist:
        last_notification_dt = None
    
    # stock from yf is more recent than last notification
    if not last_notification_dt or stock_datetime > last_notification_dt:
        if stock_price > tunnel.max_limit:
            notification = Notification(
                tunnel = tunnel,
                price = stock_price,
                datetime = stock_datetime,
                suggestion = Notification.SELL,
            )
            notification.save()
            notification_set.add(notification)
        elif stock_price < tunnel.min_limit:
            notification = Notification(
                tunnel = tunnel,
                price = stock_price,
                datetime = stock_datetime,
                suggestion = Notification.BUY,
            )
            notification.save()
            notification_set.add(notification)

def __send_emails():
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Running task for sending emails')
    if len(notification_set) != 0:
        print("Sending emails...")
        messages = []
        for notification in notification_set:
            messages.append((
                "Limite de túnel atingido",
                format_email_message(notification),
                settings.EMAIL_HOST_USER,
                [notification.tunnel.user.email],
            ))
        notification_set.clear()
        send_mass_mail(messages, fail_silently=False)
    else:
        print("No emails to send")