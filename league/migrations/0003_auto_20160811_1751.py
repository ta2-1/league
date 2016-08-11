# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_null_to_false(apps, schema_editor):
    lcc = apps.get_model("league.LeagueCompetitor").objects.filter(paid__isnull=True)
    lcc.update(paid=False)


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0002_league_is_current'),
    ]

    operations = [
        migrations.RunPython(set_null_to_false),
        migrations.AlterField(
            model_name='leaguecompetitor',
            name='paid',
            field=models.BooleanField(default=False, verbose_name='\u041e\u043f\u043b\u0430\u0442\u0438\u043b'),
        ),
        migrations.AddField(
            model_name='league',
            name='mark_unpaid_competitors',
            field=models.BooleanField(default=False, verbose_name='\u041e\u0442\u043c\u0435\u0447\u0430\u0442\u044c \u043d\u0435\u043e\u043f\u043b\u0430\u0442\u0438\u0432\u0448\u0438\u0445'),
            preserve_default=True,
        ),
    ]
