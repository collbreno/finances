class EmptyStockHistory(Exception):
    def __init__(self, msg='The provided stock symbol does not have any price history.', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)