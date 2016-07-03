# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='is_current',
            field=models.BooleanField(default=False, verbose_name='\u0422\u0435\u043a\u0443\u0449\u0430\u044f'),
            preserve_default=True,
        ),
    ]
