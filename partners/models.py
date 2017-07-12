# -*- coding: utf-8 -*-

from django.db import models


class Partner(models.Model):
    logo = models.FileField(verbose_name=u'Логотип', upload_to='partners')
    url = models.URLField(verbose_name=u'Ссылка')
    name = models.CharField(verbose_name=u'Название', max_length=255)
    label = models.CharField(verbose_name=u'Подпись', max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(verbose_name=u'Порядок', blank=True, null=True)
    is_active = models.BooleanField(verbose_name=u'Активный')

    class Meta:
        ordering = ('order', )

    def __unicode__(self):
        return self.name
