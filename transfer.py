# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 12:47:37 2018

@author: HP
"""

import sys
import getopt
import requests
import json
import datetime

# ----------------------------------------
# Static
StationMap = {'广州南':'IZQ',
              '肇庆东':'FCQ',
              '鼎湖东':'UWQ',
              '端州':'WZQ',
              '肇庆':'ZVQ',
              '佛山西':'FOQ'}
Valid_station = ['广州南', '肇庆', '端州']
# ----------------------------------------
From_station = None
To_station = None
Date = 'yyyy-mm-dd'
nearly = ''
nlate = '99:99'
# Parameters controler
for strOption, strArgument in getopt.getopt(sys.argv[1:], '', [strParameter[2:] + '=' for strParameter in sys.argv[1::2]])[0]:
    if strOption == '--from':           # from
        From_station = strArgument
    elif strOption == '--to':           # to
        To_station = strArgument
    elif strOption == '--date':         # date
        Date = strArgument
    elif strOption == '--nearly':
        nearly = strArgument
    elif strOption == '--nlate':
        nlate = strArgument

if From_station == None and To_station == None:
    raise RuntimeError('Missing [--from From_station or --to To_station], please \
                       enter where you want to start, and where is your favourite terminal.')
if not (From_station in Valid_station) or not (From_station in Valid_station):
    raise RuntimeError('I\'m sorry that this version can only support [肇庆/端州→广州南] and [广州南→肇庆/端州] temporarily.')
    
try:
    datetime.datetime.strptime(Date, '%Y-%m-%d')
except:
    raise RuntimeError('Confirm the format of [--date Date] is yyyy-mm-rr')

if nearly != '' :
    try:
        datetime.datetime.strptime(nearly, '%H:%M')
    except:
        raise RuntimeError('Confirm the format of [--nearly not_earlier_than] is hh:mm')
        
if nlate != '99:99' :
    try:
        datetime.datetime.strptime(nlate, '%H:%M')
    except:
        raise RuntimeError('Confirm the format of [--nlate not_later_than] is hh:mm')
# ----------------------------------------


def get_url(train_date='2018-12-01', from_station='WZQ', to_station='GZQ', purpose_codes='ADULT'):
    url = r'https://kyfw.12306.cn/otn/leftTicket/query?' + \
    'leftTicketDTO.train_date=' + train_date + '&' + \
    'leftTicketDTO.from_station=' + from_station + '&' + \
    'leftTicketDTO.to_station=' + to_station + '&' + \
    'purpose_codes=' + purpose_codes
    return url

def extract_info(data_str):
    info = dict()
    data = data_str.split('|')
    info['车次'] = data[3]
    info['出发地'] = data[6]
    info['目的地'] = data[7]
    info['出发时间'] = data[8]
    info['到达时间'] = data[9]
    info['历时'] = data[10]
    info['商务座/特等座'] = data[32] or data[25]
    info['一等座'] = data[31]
    info['二等座'] = data[30]
    info['高级软卧'] = data[21]
    info['软卧'] = data[23]
    info['动卧'] = data[27]
    info['硬卧'] = data[28]
    info['软座'] = data[24]
    info['硬座'] = data[29]
    info['无座'] = data[26]
    info['其他'] = data[22]
    if any(data[22:34]):
        info['是否有票'] = True
    else:
        info['是否有票'] = False
    return info

def Filter(data, train_type=None, from_station='WZQ', to_station='GZQ', skip_empty=True):
    info = []
    if type(train_type)!=list:
        train_type = [train_type]
    for i in data:
        temp_info = extract_info(i)
        if temp_info['出发时间']!='24:00' and \
           temp_info['车次'][0] in train_type and \
           temp_info['出发地']==from_station and \
           temp_info['目的地']==to_station:
            info.append(temp_info)
    return info

def delta_second(t1, t2):
    if t1 > t2:
        t1, t2 = t2, t1
    t1 = datetime.datetime(1,1,1,int(t1.split(':')[0]), int(t1.split(':')[1]))
    t2 = datetime.datetime(1,1,1,int(t2.split(':')[0]), int(t2.split(':')[1]))
    return (t2 - t1).seconds

def Advise(A_info, B_info, skip_empty=True, not_early='', not_late='99:99'):
    print('接驳方案\t时间\t\t总时间\t接驳时间')
    for a in A_info:
        at1 = a['出发时间']
        at2 = a['到达时间']
        for b in B_info:
            bt1 = b['出发时间']
            bt2 = b['到达时间']
            if at2 < bt1 and at1 > not_early and bt2 < not_late:
                h, remaind = divmod(delta_second(at1, bt2), 3600)
                m, s = divmod(remaind, 60)
                waiting_time, _ = divmod(delta_second(at2, bt1), 60)
                print('%s -> %s\t%s-%s\t%d:%d\tWaiting %d mins' % (a['车次'], b['车次'], at1, bt2, h, m, waiting_time))
                
def To_school(date='2018-12-01', start='端州', not_early='', not_late='99:99'):
    # path: 肇庆/端州 --A--> 鼎湖东 - 肇庆东 --B--> 广州南
    url = get_url(train_date=date, from_station=StationMap[start], to_station=StationMap['鼎湖东'])
    dictinfo = json.loads(requests.get(url).text)
    A_info = Filter(dictinfo['data']['result'], train_type=['C', 'D', 'G'],
                    from_station=StationMap[start], to_station=StationMap['鼎湖东'])
    
    url = get_url(train_date=date, from_station=StationMap['肇庆东'], to_station=StationMap['广州南'])
    dictinfo = json.loads(requests.get(url).text)
    B_info = Filter(dictinfo['data']['result'], train_type=['C', 'D', 'G'],
                    from_station=StationMap['肇庆东'], to_station=StationMap['广州南'])
    
    Advise(A_info, B_info, not_early=not_early, not_late=not_late)
    return A_info, B_info


# path: 广州南 --A--> 肇庆东 - 鼎湖东 --B--> 端州
def To_home(date='2018-12-01', terminal='端州', not_early='', not_late='99:99'):
    # date: yyyy-mm-dd
    url = get_url(train_date=date, from_station=StationMap['广州南'], to_station=StationMap['肇庆东'])
    dictinfo = json.loads(requests.get(url).text)
    A_info = Filter(dictinfo['data']['result'], train_type=['C', 'D', 'G'],
                    from_station=StationMap['广州南'], to_station=StationMap['肇庆东'])
    
    url = get_url(train_date=date, from_station=StationMap['鼎湖东'], to_station=StationMap[terminal])
    dictinfo = json.loads(requests.get(url).text)
    B_info = Filter(dictinfo['data']['result'], train_type=['C', 'D', 'G'],
                    from_station=StationMap['鼎湖东'], to_station=StationMap[terminal])
    Advise(A_info, B_info, not_early=not_early, not_late=not_late)
    return A_info, B_info
    
if From_station in ['肇庆', '端州']:
    A, B = To_school(date=Date, start=From_station, not_early=nearly, not_late=nlate)
elif From_station in ['广州南']:
    A, B = To_home(date=Date, terminal=To_station, not_early=nearly, not_late=nlate)
