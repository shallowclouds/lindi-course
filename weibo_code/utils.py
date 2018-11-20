
import re

limit = 100


user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
m_cookie = "_T_WM=10483ee0dc45c38eed523efea888bcae; ALF=1512609560; SCF=AquP96Utlp8YRk0uJg95bFJR8SJ9aD6FoZYo5G3aWBtE--R6WSHb4gr2i7C_3WXhuzZzQiEznJmboPTZHYfsVGo.; SUB=_2A253BXxoDeRhGeRO4lEV9ivFzTuIHXVUBgQgrDV6PUJbktBeLWzAkW1Pc5hhPY3IL00riTnWkTkHXxfMew..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W50YwhuMpEHsRAAY_PboMLz5JpX5K-hUgL.Foz71KeXSo-4SoM2dJLoI7ye9PxQ9CfjMBtt; SUHB=0xnzDYHdJqx3kN; SSOLoginState=1510018104; H5:PWA:UID=1; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D106003type%253D1%26fid%3D100103type%253D1%2526q%253Ddota2%26uicode%3D10000011"
# url = "https://m.weibo.cn/api/container/getIndex?type=all&queryVal=dota2&featurecode=20000320&luicode=10000011&lfid=106003type%3D1&title=dota2&containerid=100103type%3D1%26q%3Ddota2"
headers = {"User-Agent":user_agent,"cookie":m_cookie}


limted_time = ''
for i in range(2008,2015):
    limted_time = limted_time + str(i) + '|'
limted_time = limted_time[:-1]
re_limited_time = re.compile(limted_time)

d_cookie = "ALF=1512795836; SUB=_2A253B5HrDeRhGeRO4lEV9ivFzTuIHXVUCz-jrDV8PUJbkNBeLUvRkW2adzuZFzF5T0iGeBrk62FGeEH9EA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W50YwhuMpEHsRAAY_PboMLz5JpX5oz75NHD95QEeh.0Shqf1KqNWs4DqcjzKsHXIs-_dG2t; SINAGLOBAL=3020251936370.2905.1510205459247; httpsupgrade_ab=SSL; _s_tentry=www.baidu.com; UOR=www.baidu.com,weibo.com,www.baidu.com; Apache=989667688814.6017.1511687606193; ULV=1511687606206:5:5:1:989667688814.6017.1511687606193:1511423547830; SWBSSL=usrmdinst_3; SWB=usrmdinst_16; WBStorage=82ca67f06fa80da0|undefined"

h_headers = {"User-Agent":user_agent, "cookie": d_cookie}
