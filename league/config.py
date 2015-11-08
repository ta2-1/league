# -*- coding: utf-8 -*-
from livesettings import config_register, ConfigurationGroup, PositiveIntegerValue, StringValue

LEAGUE_GROUP = ConfigurationGroup(
    'league',               # key: internal name of the group to be created
    u'Настройки лиги',  # name: verbose name which can be automatically translated
    ordering=1             # ordering: order of group in the list (default is 1)
    )


config_register(PositiveIntegerValue(
    LEAGUE_GROUP,          
        'SOFTEN_COEF',
        description = u'Смягчающий коэффициент',              
        help_text = u'Смягчающий коэффициент',
        default = 20,
        ordering = 0        
    ))

config_register(PositiveIntegerValue(
    LEAGUE_GROUP,          
        'AVAILABLE_POSITION_DIFFERENCE',
        description = u'Допустимая разница в занимаемых позициях',              
        help_text = u'Допустимая разница в занимаемых позициях',
        default = 5,
        ordering = 1,        
    ))

config_register(PositiveIntegerValue(
    LEAGUE_GROUP,          
        'CURRENT_LEAGUE_ID',
        description = u'ID текущей лиги',              
        help_text = u'ID текущей лиги',
        default = 1,
        ordering = 1,        
    ))


config_register(PositiveIntegerValue(
    LEAGUE_GROUP,          
        'INITIAL_RATING',
        description = u'Начальный рейтинг',              
        help_text = u'Рейтинг участника перед началом розыгрыша Лиги',
        default = 100,
        ordering = 2,        
    ))

config_register(PositiveIntegerValue(
    LEAGUE_GROUP,          
        'RELIABILITY_RIVAL_QUANTITY',
        description = u'Необходимое количество соперников для присвоения места',              
        help_text = u'Необходимое количество соперников для присвоения места',
        default = 4,
        ordering = 4,        
    ))

config_register(PositiveIntegerValue(
    LEAGUE_GROUP,          
        'FINAL_RIVAL_QUANTITY',
        description = u'Необходимое количество соперников для присвоения итогового места',              
        help_text = u'Необходимое количество соперников для присвоения итогового места',
        default = 10,
        ordering = 5,
    ))

config_register(StringValue(
    LEAGUE_GROUP,
        'N_FORMULA',
        description = u'Формула N',
        help_text = u'N',
        default = 'result1 - result2',
        ordering = 6
    ))

config_register(StringValue(
    LEAGUE_GROUP,          
        'DELTA_FORMULA',
        description = u'Формула DELTA',              
        help_text = u'r1 r2 N',
        default = 'N + (r2-r1)/SOFTEN_COEF',
        ordering = 7,        
    ))

