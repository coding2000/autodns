#!/usr/bin/env python  
# -*- coding:utf-8 -*- 

token = '56xxxx,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

ltop = ["编号", "域名", "等级", "状态", "记录", "更新"]
rl = ["编号", "子域名", "记录值", "记录类型", "线路", "状态", "MX", "TTL"]

grade_list = {
    'D_Free': u'免费套餐',
    'D_Plus': u'豪华 VIP套餐',
    'D_Extra': u'企业I VIP套餐',
    'D_Expert': u'企业II VIP套餐',
    'D_Ultra': u'企业III VIP套餐',
    'DP_Free': u'新免费套餐',
    'DP_Plus': u'个人专业版',
    'DP_Extra': u'企业创业版',
    'DP_Expert': u'企业标准版',
    'DP_Ultra': u'企业旗舰版',
}

status_list = {
    'enable': u'启用',
    'pause': u'暂停',
    'spam': u'封禁',
    'lock': u'锁定',
}


