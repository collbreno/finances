from django.db import models

class Person(models.Model):
    email = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.email
    
class PersonStock(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=20)
    min_limit = models.FloatField()
    max_limit = models.FloatField()
    time_interval = models.IntegerField()

    def __str__(self):
        return (f'{self.person} watching {self.stock_symbol} ' 
                f'[{self.min_limit},{self.max_limit}] ' 
                f'{self.time_interval}min')
    