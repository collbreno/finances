import yahooquery as yq
import locale

from .exceptions import EmptyStockHistory
from .models import Notification

def download_stock_history(stock_symbol: str):
    ticker = yq.Ticker(stock_symbol).history(period='1d', interval='1m')
    if ticker.empty:
        raise EmptyStockHistory()
    return ticker.reset_index()[['date', 'close']].rename(columns={'date':'datetime', 'close': 'price'})

def get_stock_data(stock_symbol: str):
    df = download_stock_history(stock_symbol)
    graph_data = {
        'x': df['datetime'].dt.strftime('%H:%M').tolist(),
        'y': df['price'].tolist(),
    }

    return {
        'graph_data': graph_data,
        'date': df['datetime'].iloc[-1].strftime('%d/%m/%Y'),
    }

def format_stock_symbol(original: str):
    return original.replace("<em>", "").replace("</em>", "")+".SA".upper()

def format_email_message(notification: Notification):
    user = notification.tunnel.user
    stock_symbol = notification.tunnel.stock_symbol
    formatted_datetime = notification.datetime.strftime('%d/%m/%Y %H:%M')
    message = (f"Oi {user.name}!\n"
               f"O limite do seu túnel#{notification.tunnel.id} definido para a ação {stock_symbol} "
               f"foi atingido em {formatted_datetime}. Você deve "
               f"{notification.get_suggestion_display().upper()} a ação por "
               f"{format_currency(notification.price)}.")
    return message

def format_currency(price):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    return locale.currency(price)
