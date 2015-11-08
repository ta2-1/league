# -*- coding: utf-8 -*-
from livesettings import config_register, ConfigurationGroup, PositiveIntegerValue, StringValue, LongStringValue
#from django.utils.translation import ugettext_lazy as _

# First, setup a grup to hold all our possible configs
RATING_GROUP = ConfigurationGroup(
    'rating',               # key: internal name of the group to be created
    u'Настройки',  # name: verbose name which can be automatically translated
    ordering=0             # ordering: order of group in the list (default is 1)
    )

# Now, add our number of images to display value
# If a user doesn't enter a value, default to 5
#RATING_MAX_COMPETITORS_COUNT = 32
#RATING_LAST_TOURNAMENTS_COUNT = 8
#RATING_RESULT_TOURNAMENTS_COUNT = 4

config_register(PositiveIntegerValue(
    RATING_GROUP,          
        'MAX_COMPETITORS_COUNT',
        description = u'Количество участников (var - rmc_count)',              
        help_text = u'Максимальное количество участников в турнире',
        default = 32,
        ordering = 0        
    ))

config_register(PositiveIntegerValue(
    RATING_GROUP,           
        'LAST_TOURNAMENTS_COUNT',
        description = u'Количество турниров до обнуления результатов (var - rlt_count)',     
        default = 8,
        ordering = 1          
    ))

config_register(PositiveIntegerValue(
    RATING_GROUP,           
        'RESULT_TOURNAMENTS_COUNT',
        description = u'Учитываемое количество турниров (var - rt_count)',
        help_text = u'Результаты скольких последних турниров учитываются при расчете рейтинга участника',     
        default = 4,
        ordering = 2  
    ))

config_register(LongStringValue(
    RATING_GROUP,           
        'R_PLACE',
        description = u'Среднее место (r_place)',
        help_text = u'place - занятое место, tc_count - количество участников в турнире',     
        default = u'round(place * rmc_count / tc_count)',
        ordering = 3
    ))


config_register(LongStringValue(
    RATING_GROUP,           
        'Y',
        description = 'Y',
        #help_text = u'Пример: c_count - r_place + 1',
        default = 'rmc_count - r_place + 1',
        ordering = 4     
    ))

config_register(LongStringValue(
    RATING_GROUP,           
        'X',
        description = 'X',
        help_text = u't_number - номер турнира в обратном порядке',
        default = 'rlt_count - t_number + 1',
        ordering = 5     
    ))

MAIN_FORMULA_GROUP = ConfigurationGroup(
    #RATING_GROUP,
    'rating_main_formula', # key: internal name of the group to be created
    u'Основная фомула',  # name: verbose name which can be automatically translated
    ordering=1             # ordering: order of group in the list (default is 1)
    )


config_register(LongStringValue(
    MAIN_FORMULA_GROUP,           
        'MAIN_FORMULA_VALUE',
        description = u'Формула',
        #help_text = u'Пример: Y*(Y-1)*lt_count/2 + X*Y',
        default = 'Y*(Y-1)*rlt_count/2 + X*Y'     
    ))

ITERATE_FORMULA_GROUP = ConfigurationGroup(
    #RATING_GROUP,
    'rating_iterate_formula',   # key: internal name of the group to be created
    u'Рекурсивная формула',   # name: verbose name which can be automatically translated
    ordering=2                  # ordering: order of group in the list (default is 1)
    )

config_register(LongStringValue(
    ITERATE_FORMULA_GROUP,           
        'ITERATE_FORMULA_VALUE',
        description = u'Формула A[i]',
        #help_text = u'Пример: A[i-1] + (i-1)*lt_count + 1',
        default = 'A[i-1] + (i-1)*lt_count + 1'     
    ))

config_register(StringValue(
    ITERATE_FORMULA_GROUP,           
        'ITERATOR_VALUE',
        description = u'Итератор (i)',
        #help_text = u'Пример: X*Y+X',
        default = 'X*Y+X'     
    ))