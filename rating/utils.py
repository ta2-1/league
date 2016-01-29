# -*- coding: utf-8 -*-

import re

def get_place(place):
    if re.match(r'^\d+$', str(place)) != None:
        rplace = place
    else:
        places = re.match(r'(\d+)\s*-\s*(\d+)', place)
        if places != None:
            rplace = round((int(places.group(1))+int(places.group(2)))/2)
        else:
            rplace = -1
            
    return int(rplace)

def get_upbound_place(place):
    
    if re.match(r'^\d+$', place) != None:
        rplace = place
    else:
        places = re.match(r'(\d+)\s*-\s*(\d+)', place)
        if places != None:
            rplace = int(places.group(2))
        else:
            rplace = -1
            
    return int(rplace)

def get_last_place(place_list):
    max = 0
    for d in place_list:
        if place_list[d]['rating'] > 0 and max < get_upbound_place(place_list[d]['place']):
            max = get_upbound_place(place_list[d]['place'])

    return max

def get_place_delta(place_list, place_list1, competitor_id):
    try:
        if place_list1[competitor_id]['rating'] == 0:
            if place_list[competitor_id]['rating'] == 0:
                res = '*'
            else:
                res = get_last_place(place_list1) - get_place(place_list[competitor_id]['place'])
        else:   
            if place_list[competitor_id]['rating'] == 0:
                res = get_place(place_list1[competitor_id]['place']) - get_last_place(place_list) 
            else:
                res = get_place(place_list1[competitor_id]['place']) - get_place(place_list[competitor_id]['place'])
    except:
        res = '*' 
    
    return res

def get_place_from_list(place_list, competitor_id):
    try:
        res = place_list[competitor_id]['place']
    except:
        res = '*' 
    
    return res

def get_points_by_params(object, r_place, t_number, rmc_count, rlt_count):
    Y = rmc_count - r_place + 1
    X = rlt_count - t_number + 1

    if t_number > rlt_count:
        return (object, 0, False) #(competitor_object, rating_value, included in result)
    elif t_number <= 0:
        return (object, 0, False)
    else:
        return (object, int(Y*(Y-1)*rlt_count/2 + X*Y), True)
    
def get_points(object, rmc_count, rlt_count, back_offset_number=0):
    place = get_place(object.place)
    tc_count = object.resultset.competitors.count()
    t_number = object.resultset.sequence_number() - back_offset_number
    r_place = int(round(place * rmc_count / tc_count))
    
    return get_points_by_params(object, r_place, t_number, rmc_count, rlt_count)
    
    #4224-((66-rplace)*(rplace-1)*4+(number-1)*(33-rplace)
    
def get_rating(competitor, category_id, back_offset_number = 0):
    return competitor.rating_by_category(category_id, back_offset_number)    
    
"""
    вычисляет место (диапазон мест) игрока по его 
    индексу в отсортированном по рейтингу списке 
"""
def get_place_from_rating_list(rating_list, i):
    if rating_list[i]['rating'] == 0:
        return "-"
    
    jmin = 0
    jmax = 0
    
    while len(rating_list) > i+jmax+1 and rating_list[i]['rating'] == rating_list[i+jmax+1]['rating']:
        jmax += 1
    
    while i-jmin-1 >= 0 and rating_list[i]['rating'] == rating_list[i-jmin-1]['rating']:
        jmin += 1
    
    if jmax > 0 or jmin > 0:
        data = "%d-%d" % (i-jmin+1, i+1+jmax)    
    else:
        data = "%d" % (i+1)
        
    return data
