import yahooquery as yq
import json

def download_stock(stock_symbol: str):
    ticker = yq.Ticker(stock_symbol).history(period='1d', interval='1m')
    return ticker.reset_index()[['date', 'close']].rename(columns={'date':'datetime', 'close': 'price'})

def get_stock_graph_data(stock_symbol: str):
    df = download_stock(stock_symbol)
    graph_data = {
        'x': df['datetime'].dt.strftime('%H:%M').tolist(),
        'y': df['price'].tolist(),
    }

    return graph_data