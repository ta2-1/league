# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-03 08:47
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import migrations, models


def set_statements(apps, schema_editor):
    for league in apps.get_model("league.League").objects.all():
        url = reverse('league_statement', args=[league.id])
        fp = apps.get_model("flatpages.Flatpage").objects.filter(url=url).first()
        if fp:
            league.statement = fp
            league.save()


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0007_league_statement'),
    ]

    operations = [
        migrations.RunPython(set_statements),
    ]
