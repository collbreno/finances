# Generated by Django 4.2.6 on 2023-10-13 04:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0004_rename_person_user_rename_person_tunnel_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currentPrice', models.DecimalField(decimal_places=2, max_digits=10)),
                ('datetime', models.DateTimeField()),
                ('suggestion', models.CharField(choices=[('B', 'Comprar'), ('S', 'Vender')], max_length=1)),
                ('tunnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.tunnel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finances.user')),
            ],
        ),
    ]
