import json
import requests

from django.http import JsonResponse
from django.shortcuts import render

from ..models import Tunnel
from ..utils import get_stock_data, format_stock_symbol, format_currency
from ..exceptions import EmptyStockHistory

def stocks_page(request):
    return render(request, "finances/stocks.html")

def stock_page(request, stock_symbol):
    try:
        stock_data = get_stock_data(stock_symbol)
    except EmptyStockHistory:
        context = {
            'error_message': f'A ação {stock_symbol} não possui histórico de preço.'
        }
        return render(request, 'finances/error_page.html', context)
    
    tunnels = Tunnel.objects.filter(stock_symbol=stock_symbol)
    graph_data = stock_data['graph_data']

    context = {
        'graph_data': json.dumps(graph_data),
        'stock_symbol': stock_symbol.upper(),
        'tunnels': tunnels,
        'last_price': format_currency(graph_data['y'][-1]),
        'last_price_time': graph_data['x'][-1],
        'date': stock_data['date'],
    }

    return render(request, 'finances/stock.html', context)

def get_symbol_suggestions(request):
    query = request.GET.get('query', '')
    url = 'https://symbol-search.tradingview.com/symbol_search/v3/'
    params = {
        'sort_by_country': 'BR',
        'domain': 'bovespa',
        'start': 0,
        'search_type': 'undefined',
        'lang': 'pt',
        'hl': 1,
        'text': query
    }

    response = requests.get(url, params=params)
    response_data = response.json()

    symbols = [format_stock_symbol(item['symbol']) for item in response_data.get('symbols', [])]

    return JsonResponse({'symbols': json.dumps(symbols)})


