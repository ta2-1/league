# -*- coding: utf-8 -*-

from django import template
from math import fabs
import re

from rating.models import Competitor
from django.core.urlresolvers import resolve as django_resolve

register = template.Library()

@register.filter
def get_competitor_attr(value, arg):
    c = Competitor.objects.get(id=value)
    return getattr(c, arg)
 
@register.filter
def show_sign(value):
    try:
        i = int(value)
        if i > 0:
            return "<span class='positive' style='color:#0A0;'>+%d</span>" % i
        elif i < 0:
            return "<span class='negative' style='color:#D00;'>%d</span>" % i
        else:
            return "<span class='zero'>0</span>"
    except:
        return ''
    
@register.filter
def show_floatformat_sign(value):
    try:
        s = value.replace(',', '.')
        v = float(s)
        if v > 0:
            return "<span class='positive' style='color:#0A0;'>+%s</span>" % value
        elif v < 0:
            return "<span class='negative' style='color:#D00;'>%s</span>" % value
        else:
            return "<span class='zero'>0</span>"
    except:
        return ''

@register.filter
def show_arrow(value):
    try:
        i = int(value)
        if i > 0:
            return "<span class='positive' style='color:#0A0;'>%d&uarr;</span>" % i
        elif i < 0:
            return "<span class='negative' style='color:#D00;'>%d&darr;</span>" % fabs(i)
        else: 
            return "<span class='zero'>0</span>"
    except:
        return "*"
    
@register.filter
def contains(value, arg):
    """
    Usage:
    {% if text|contains:"http://" %}
          This is a link.
    {% else %}
          Not a link.
    {% endif %}
    """
  
    return arg in value 

@register.filter
def score(value, arg):
    """
        value - games_count
        arg - wins_count
    """
    return "%d : %d" % (int(value) - int(arg), int(arg)) 

@register.filter
def match(value, arg):
    if value is None:
        return False

    prog = re.compile(arg)
    return prog.match(value) != None

@register.filter
def resolved_url_name(value):
    r = django_resolve(value)
    
    return r.url_name

@register.filter
def is_in(value, args):
    if args is None:
        return False
    
    arg_list = [arg.strip() for arg in args.split(',')]
    
    return value in arg_list
    
@register.filter
def win_or_lose(value, arg):
    if value > arg:
        return 'win'
    else:
        return 'lose'
