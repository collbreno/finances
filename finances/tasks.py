from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .models import Tunnel, Notification
from .utils import download_stock


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
    print(f'Adicionei task do tunel {tunnel.id}')

def check_tunnel(tunnel: Tunnel):
    print('rodando task do tunnel')
    stock_symbol = tunnel.stock_symbol
    history = download_stock(stock_symbol)
    stock_datetime = history['datetime'].iloc[-1]
    stock_price = history['price'].iloc[-1]

    try:
        last_notification_dt = Notification.objects.filter(tunnel__stock_symbol=stock_symbol).latest('datetime').datetime
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