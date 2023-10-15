from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import send_mail
from django.conf import settings
from django.core import mail
from datetime import datetime

from .models import Tunnel, Notification
from .utils import download_stock_history, format_email_message

print('Getting mail connection...')
mail_connection = mail.get_connection()
print('Opening connection...')
mail_connection.open()
print('Connection open!')

def schedule_tasks_for_existing_tunnels(scheduler: BlockingScheduler):
    tunnels = Tunnel.objects.all()
    for tunnel in tunnels:
        watch_tunnel(scheduler, tunnel)
    scheduler.start()

def watch_tunnel(scheduler: BlockingScheduler, tunnel: Tunnel):
    scheduler.add_job(
        check_tunnel,
        args=(tunnel,),
        trigger=CronTrigger(second=f"*/{tunnel.time_interval}"),
        id=f'tunnel#{tunnel.id}',
        max_instances=1,
        replace_existing=True,
    )
    print(f'Task added for tunnel#{tunnel.id} ({tunnel.stock_symbol})')

def check_tunnel(tunnel: Tunnel):
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
        print(f"Stock {stock_symbol} has new price!")
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
    else:
        print(f"Stock {stock_symbol} doesn't have updated price")

def __send_email(notification: Notification):
    print('Sending email...')
    send_mail(
        subject="Limite de túnel atingido",
        from_email=settings.EMAIL_HOST_USER,
        message=format_email_message(notification),
        recipient_list=[notification.tunnel.user.email],
        fail_silently=False,
        connection=mail_connection
    )