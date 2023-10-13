from django.db import models

class User(models.Model):
    email = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.email
    
class Tunnel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=20)
    min_limit = models.DecimalField(max_digits=10, decimal_places=2)
    max_limit = models.DecimalField(max_digits=10, decimal_places=2)
    time_interval = models.IntegerField()

    def __str__(self):
        return (f'{self.user} watching {self.stock_symbol} ' 
                f'[{self.min_limit},{self.max_limit}] ' 
                f'{self.time_interval}min')
    
class Notification(models.Model):
    BUY = "B"
    SELL = "S"
    OPTIONS = [
        (BUY, "Comprar"),
        (SELL, "Vender"),
    ]

    tunnel = models.ForeignKey(Tunnel, on_delete=models.CASCADE)
    currentPrice = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField()
    suggestion = models.CharField(max_length=1, choices=OPTIONS)
    