import requests
from bs4 import BeautifulSoup
import re
import json
#from __future__ import print_function
import os
import time
import utils
import pandas as pd
import numpy as np
import glob
import codecs
# limit = 100


# used to send requests

import utils



from sousuo import *

# read the csv file and return
def imptexts(path,start):
   f = open(path,'r')
   fileList = f.readlines()[start:]
   return fileList;


def scrapy_info_mid(keyword, mid_list):
    '''
    scrapy info with bid
    param:
        keyword: string
        bid_list: list or DataFrame
    '''
    
    print("scrapy keyword :%s's web info"%(keyword))
    rootdir = "data/"

    rootdir = rootdir + "keyword_" + keyword + "/"
    os.mkdir(rootdir[:-1])
    search_result = get_blog_with_mid(mid_list)
    if search_result is None or len(search_result) == 0:
        return None
    search_result['uid'].dropna(inplace = True)
    #保存搜索微博结果
    print(rootdir)
    search_result.to_csv(rootdir + keyword+"_search_blog.csv",sep='\001',index = False)
    #scrapy user's personal information
    user_result = get_user_infos(search_result['uid'].values)
    #add the directory of blog and follower
    #############################I delete it
#    user_result['blog_dir'] = user_result['uid'].apply(lambda x:"uid_"+str(x)+"/blog.csv")
    user_result['follower_dir'] = user_result['uid'].apply(lambda x:"uid_"+str(x)+"/followers.csv")
    #save user result
    user_result.to_csv(rootdir + keyword+"_user_info.csv",index = False,sep='\t')
    #make specific directory for each user
    for i in user_result.uid.unique():
        print(rootdir + "uid_" + str(i))
        os.mkdir(rootdir + "uid_"+str(i))
    get_followers_info(rootdir,user_result.uid.unique())
    #############################I delete it
#    get_blogs_info(rootdir,user_result.uid.unique())
    # 对搜出的每条微博　爬取转发和评论
    for idx in search_result.index:
        get_reposts_info(rootdir, search_result.ix[idx,'uid'], search_result.ix[idx:idx,'mid'], search_result.ix[idx:idx,'reposts_count'])
        get_comments_info(rootdir, search_result.ix[idx,'uid'], search_result.ix[idx:idx,'mid'], search_result.ix[idx:idx,'comments_count'])

    #return to the upper folder
    # os.chdir("..")
    print("finish scrapy keyword :%s's, using time %d"%(keyword,time.time() - start_time))
    return None

if __name__=="__main__":
    # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    # m_cookie = "_T_WM=10483ee0dc45c38eed523efea888bcae; ALF=1512609560; SCF=AquP96Utlp8YRk0uJg95bFJR8SJ9aD6FoZYo5G3aWBtE--R6WSHb4gr2i7C_3WXhuzZzQiEznJmboPTZHYfsVGo.; SUB=_2A253BXxoDeRhGeRO4lEV9ivFzTuIHXVUBgQgrDV6PUJbktBeLWzAkW1Pc5hhPY3IL00riTnWkTkHXxfMew..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W50YwhuMpEHsRAAY_PboMLz5JpX5K-hUgL.Foz71KeXSo-4SoM2dJLoI7ye9PxQ9CfjMBtt; SUHB=0xnzDYHdJqx3kN; SSOLoginState=1510018104; H5:PWA:UID=1; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D106003type%253D1%26fid%3D100103type%253D1%2526q%253Ddota2%26uicode%3D10000011"
    # # url = "https://m.weibo.cn/api/container/getIndex?type=all&queryVal=dota2&featurecode=20000320&luicode=10000011&lfid=106003type%3D1&title=dota2&containerid=100103type%3D1%26q%3Ddota2"
    # headers = {"User-Agent":user_agent,"cookie":m_cookie}
    # content = requests.get(url,headers = headers)
    # content = content.content.decode('utf-8','ignore')
    # keywords = []
    # with open("keywords.txt",'r') as f: 
    #     result = f.read().split('\n')
    #     keywords.extend(result)
    #
    # for i,j in enumerate(keywords):
    #     keywords[i] = j+" 文玩"
    # for keyword in keywords:
    #     scrapy_info(keyword,headers)
    
    #'犀角 安宫牛黄丸',
     
#    for key in keywords:
#        scrapy_info(key[0])
        
	
#    for key in keywords:
#        scrapy_info(key)


    path="keylist.csv"
    try:        
        temp = imptexts(path,0)
        documents1 = []

        for i in range(len(temp)):
            document1 = []
            document0 = temp[i].split(',')
            document1.append(document0[0])
            document1.append(document0[1])
            documents1.append(document1)

        print(documents1)

        final_data1 = pd.DataFrame(documents1);

        print(final_data1)

        old_names = list(range(2))
        new_names = ['keyword', 'mid']

        final_data1.rename(columns=dict(zip(old_names, new_names)), inplace=True)
        final_data1 = final_data1[new_names]
        #    final_data1= final_data1.drop_duplicates(['mid'])

        keywords = list(final_data1['keyword'])
        MID = list(final_data1['mid'])
        tempkey = list(set(keywords))

        documents = []
        for key in tempkey:
            document = []
            document1 = []
            for i in range(len(keywords)):
                if key == keywords[i]:
                    document.append(MID[i])
            document1.append(key)
            document1.append(document)
            documents.append(document1)

        for key in documents:
            temp = []
            for tempkey in key[1]:
                a = tempkey.split('/')[-1]
                a = a.strip('\n')
                temp.append(a)
            scrapy_info_mid(key[0], temp)

    except IOError:
        print("io err")
        pass


  
		
