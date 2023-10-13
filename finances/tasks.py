import yfinance as yf

from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .models import Tunnel, Notification

scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)

def schedule_tasks_for_existing_tunnels():
    tunnels = Tunnel.objects.all()
    for tunnel in tunnels:
        watch_tunnel(tunnel)
    scheduler.start()

def watch_tunnel(tunnel: Tunnel):
    scheduler.add_job(
        check_tunnel,
        args=(tunnel,),
        trigger=CronTrigger(second="*/5"),
        id=f'tunnel#{tunnel.id}',
        max_instances=1,
    )
    print(f'Adicionei task do tunel {tunnel.id}')

def check_tunnel(tunnel: Tunnel):
    print('rodando task do tunnel')
    stock_symbol = tunnel.stock_symbol
    history = yf.download(stock_symbol, period='1day', interval='1m')
    stock_datetime = history.index[-1]
    stock_price = history['Close'][-1]

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
            send_email(notification)
        elif stock_price < tunnel.min_limit:
            notification = Notification(
                tunnel = tunnel,
                price = stock_price,
                datetime = stock_datetime,
                suggestion = Notification.BUY,
            )
            notification.save()
            send_email(notification)
    else:
        print(f"Stock {stock_symbol} doesn't have updated price")

def send_email(notification: Notification):
    print(f"Sending email: {notification}")
    #TODO: implement email