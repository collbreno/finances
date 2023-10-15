from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler import util
from django.core.mail import send_mail
from django.conf import settings
from django.core import mail
from datetime import datetime

from .models import Tunnel, Notification
from .utils import download_stock_history, format_email_message

print('Creating scheduler...')
scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
print('Scheduler created!')
print('Getting mail connection...')
mail_connection = mail.get_connection()
print('Opening connection...')
mail_connection.open()
print('Connection open!')
tunnel_id_set = set()

def schedule_database_watcher():
    scheduler.add_jobstore(DjangoJobStore(), "default")
    print("Scheduling database watcher")
    scheduler.add_job(
        __watch_database,
        #TODO: change to 1 minute
        trigger=CronTrigger(second="*/10"),
        id='database_watcher',
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
        #TODO: change to minutes
        trigger=CronTrigger(second=f"*/{tunnel.time_interval}"),
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
            __send_email(notification)
        elif stock_price < tunnel.min_limit:
            notification = Notification(
                tunnel = tunnel,
                price = stock_price,
                datetime = stock_datetime,
                suggestion = Notification.BUY,
            )
            notification.save()
            __send_email(notification)

def __send_email(notification: Notification):
    print(f'Sending email... (tunnel#{notification.tunnel.id})')
    send_mail(
        subject="Limite de túnel atingido",
        from_email=settings.EMAIL_HOST_USER,
        message=format_email_message(notification),
        recipient_list=[notification.tunnel.user.email],
        fail_silently=False,
        connection=mail_connection
    )