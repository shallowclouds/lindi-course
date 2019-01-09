'''
This file is used to scrapy some information from weibo
1. use personal cookie to login
2. use its search engine to search some keyword
3. scrapy the result and scrapy each user's information (including personal information and all of its blogs) in the search result

'''









'''
20171125 version:

1. 改 userinfo 信息 加大V 认证, 加粉丝数量, 加认证的描述, 加关注人数量  1
2. 改 userinfo 信息 加用户特征标签  1
3. 加爬评论模块 1
4. 加正则表达式 限制时间   1
5. 更改结构,爬search info 的repost 和comment 1
6. 输出按是否大V, 粉丝数量排序 1
7. search 增加多几页







'''
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
import utils
import pandas as pd
import numpy as np
import glob
# limit = 100











# maybe this func went wrong,let's test
def scrapy_info(keyword):
    start_time = time.time()
    print("scrapy keyword :%s's web info"%(keyword))
    #make spceific direcory for the keyword
    rootdir = "data/"   # keyword 目录

    try:
        os.mkdir(rootdir + "keyword_"+keyword)  #针对一个新的　keyword
    # os.chdir("keyword_"+keyword)

    #scrapy the search result
    except Exception:
        print("the file exists")
        pass

    rootdir = rootdir + "keyword_" + keyword + "/"
    search_result = get_search(keyword)

    if search_result is None or len(search_result) == 0:
        # os.chdir("..")
        print("search result: Nothing")
        return None
    search_result['uid'].dropna(inplace = True)
    #保存搜索微博结果
    search_result.to_csv(rootdir + keyword+"_search_blog.csv",sep='\t',index = False)
    #scrapy user's personal information
    user_result = get_user_infos(search_result['uid'].values)
    #add the directory of blog and follower
    user_result['blog_dir'] = user_result['uid'].apply(lambda x:"uid_"+str(x)+"/blog.csv")
    user_result['follower_dir'] = user_result['uid'].apply(lambda x:"uid_"+str(x)+"/followers.csv")
    #save user result
    user_result.to_csv(rootdir + keyword+"_user_info.csv",index = False,sep='\t')
    #make specific directory for each user
    for i in user_result.uid.unique():
        try:
            print(rootdir + "uid_" + str(i))
            os.mkdir(rootdir + "uid_"+str(i))
        except Exception:
            print("it seems the file already exists")
    get_followers_info(rootdir,user_result.uid.unique())
    get_blogs_info(rootdir,user_result.uid.unique())
    # 对搜出的每条微博　爬取转发和评论
    for idx in search_result.index:
        get_reposts_info(rootdir, search_result.ix[idx,'uid'], search_result.ix[idx:idx,'bid'], search_result.ix[idx:idx,'reposts_count'])
        get_comments_info(rootdir, search_result.ix[idx,'uid'], search_result.ix[idx:idx,'bid'], search_result.ix[idx:idx,'comments_count'])

    #return to the upper folder
    # os.chdir("..")
    print("finish scrapy keyword :%s's, using time %d"%(keyword,time.time() - start_time))
    return None

def scrapy_info_uid(keyword, uid_list):
    '''
    scrapy userinfo and its followers with keyword and uidlist
    param:
        keyword: string
        uid_list: list or DataFrame
    '''


    start_time = time.time()
    print("scrapy keyword :%s's web info"%(keyword))
    rootdir = "data/"

    os.mkdir(rootdir + "keyword_uid_" + keyword)
    rootdir  = rootdir + "keyword_uid_" + keyword + "/"
    uid_list = pd.DataFrame(uid_list.values)
    uid_list.index = np.arange(len(uid_list))
    user_result = get_user_infos(list(uid_list[0].values))
    user_result['follower_dir'] = user_result['uid'].apply(lambda x:"uid_"+str(x)+"/followers.csv")
    user_result.to_csv(rootdir + keyword+"_user_info.csv",index = False,sep='\t')
    for i in user_result.uid.unique():
        # print(rootdir + "uid_" + str(i))
        os.mkdir(rootdir + "uid_"+str(i))
    get_followers_info(rootdir,user_result.uid.unique())
    print("finish scrapy keyword :%s's, using time %d"%(keyword,time.time() - start_time))
    return None

def scrapy_info_mid(keyword, mid_list):
    '''
    scrapy info with bid
    param:
        keyword: string
        bid_list: list or DataFrame
    '''
    start_time = time.time()
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




def get_single_blog_web(mid):
    url = "https://m.weibo.cn/status/" + mid
    try:
        bsoj = requests.get(url,utils.headers).content.decode('utf-8','ignore')
        ######
        bsoj = BeautifulSoup(bsoj,'lxml')
        # add param lxml
        return str(bsoj.body.script)
    except:
        print("Get " + url + "failed")
        return None


def get_single_blog_info(web_str):
    tags = ['mid','text','scheme','created_at','source','reposts_count','comments_count','pid']
    user_tags = ['id','screen_name','profile_url','verified_type','verified_reason','description','followers_count','gender']
    # retweeted = ['mid','text']
    blog = dict()
    for i in tags:
        blog[i] = ''
        blog["retweeted_"+i] = ""
    for i in user_tags:
        blog[i] = ""
        blog["retweeted_"+i] = ""
    for i in tags:
        re_i = re.compile( "\"" +i + "\": (.+),\n")
        result = re.findall(re_i,web_str)
        if len(result)>0:
            # blog[i] = result[0]
            temp = result[0]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
        if len(result) > 2:
            temp = result[1]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
    for i in user_tags:
        re_i = re.compile("\"" + i + "\":(.+),\n")
        result = re.findall(re_i,web_str)
        origin_index = 0
        retweeted_index = 1
        if i == 'id':
            origin_index+=1
            retweeted_index+=2
        if len(result)>0:
            temp = result[origin_index]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
        if len(result)>retweeted_index:
            temp = result[retweeted_index]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
    blog.pop('retweeted_pid')
    if(blog['pid']!=''):   # pid 指照片id 有为1 没有为0
        blog['pid'] = 1
    else:
        blog['pid'] = 0
    blog['uid'] = blog['id'][1:]
    blog.pop('id')
    blog['retweeted_uid'] = blog['retweeted_id'][1:]
    blog.pop('retweeted_id')
    # blog['bid'] = blog['mid']
    return blog

def scrapy_info_mid(keyword, mid_list):
    '''
    scrapy info with bid
    param:
        keyword: string
        bid_list: list or DataFrame
    '''
    start_time = time.time()
    print("scrapy keyword :%s's web info"%(keyword))
    rootdir = "data/"

    rootdir = rootdir + "keyword_" + keyword + "/"
    os.mkdir(rootdir[:-1])
    search_result = get_blog_with_mid(mid_list)
    if search_result is None or len(search_result) == 0:
        # os.chdir("..")
        return None
    search_result['uid'].dropna(inplace = True)
    #保存搜索微博结果
    print(rootdir)
#    search_result.to_csv(rootdir + keyword+"_search_blog.csv",sep='\001',index = False)
    #scrapy user's personal information
    user_result = get_user_infos(search_result['uid'].values)
    #add the directory of blog and follower
#    user_result['blog_dir'] = user_result['uid'].apply(lambda x:"uid_"+str(x)+"/blog.csv")
#    user_result['follower_dir'] = user_result['uid'].apply(lambda x:"uid_"+str(x)+"/followers.csv")
    #save user result
    user_result.to_csv(rootdir + keyword+"_user_info.csv",index = False,sep='\t')
    #make specific directory for each user
#    for i in user_result.uid.unique():
#        print(rootdir + "uid_" + str(i))
#        os.mkdir(rootdir + "uid_"+str(i))
#    get_followers_info(rootdir,user_result.uid.unique())
#    get_blogs_info(rootdir,user_result.uid.unique())
    # 对搜出的每条微博　爬取转发和评论
#    for idx in search_result.index:
#        get_reposts_info(rootdir, search_result.ix[idx,'uid'], search_result.ix[idx:idx,'mid'], search_result.ix[idx:idx,'reposts_count'])
#        get_comments_info(rootdir, search_result.ix[idx,'uid'], search_result.ix[idx:idx,'mid'], search_result.ix[idx:idx,'comments_count'])

    #return to the upper folder
    # os.chdir("..")
    print("finish scrapy keyword :%s's, using time %d"%(keyword,time.time() - start_time))
    return None




def get_single_blog_web(mid):
    url = "https://m.weibo.cn/status/" + mid
    try:
        bsoj = requests.get(url,utils.headers).content.decode('utf-8','ignore')
        ######
        bsoj = BeautifulSoup(bsoj,'lxml')
        # add param lxml
        return str(bsoj.body.script)
    except:
        print("Get " + url + "failed")
        return None


def get_single_blog_info(web_str):
    tags = ['mid','text','scheme','created_at','source','reposts_count','comments_count','pid']
    user_tags = ['id','screen_name','profile_url','verified_type','verified_reason','description','followers_count','gender']
    # retweeted = ['mid','text']
    blog = dict()
    for i in tags:
        blog[i] = ''
        blog["retweeted_"+i] = ""
    for i in user_tags:
        blog[i] = ""
        blog["retweeted_"+i] = ""
    for i in tags:
        re_i = re.compile( "\"" +i + "\": (.+),\n")
        result = re.findall(re_i,web_str)
        if len(result)>0:
            # blog[i] = result[0]
            temp = result[0]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
        if len(result) > 2:
            temp = result[1]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
    for i in user_tags:
        re_i = re.compile("\"" + i + "\":(.+),\n")
        result = re.findall(re_i,web_str)
        origin_index = 0
        retweeted_index = 1
        if i == 'id':
            origin_index+=1
            retweeted_index+=2
        if len(result)>0:
            temp = result[origin_index]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
        if len(result)>retweeted_index:
            temp = result[retweeted_index]
            if(temp[0] == '"'):
                temp = temp[1:-1]
            blog[i] = temp
    blog.pop('retweeted_pid')
    if(blog['pid']!=''):   # pid 指照片id 有为1 没有为0
        blog['pid'] = 1
    else:
        blog['pid'] = 0
    blog['uid'] = blog['id'][1:]
    blog.pop('id')
    blog['retweeted_uid'] = blog['retweeted_id'][1:]
    blog.pop('retweeted_id')
    # blog['bid'] = blog['mid']
    return blog


def get_blog_with_mid(mid_list):
    blogs = []
    for i in mid_list:
        web_str = get_single_blog_web(i)
        blog = get_single_blog_info(web_str)
        if blog['mid'] != '':
            blogs.append(blog)
        else:
            print("get %s blog information failed"%(i))
    return pd.DataFrame(blogs)	

def get_blog_with_mid(mid_list):
    blogs = []
    for i in mid_list:
        web_str = get_single_blog_web(i)
        blog = get_single_blog_info(web_str)
        if blog['mid'] != '':
            blogs.append(blog)
        else:
            print("get %s blog information failed"%(i))
    return pd.DataFrame(blogs)


def get_info(url,headers):
    """
    use requests to scrapy the web page
    url : the url you want to scrapy    -- type:"str"
    headers : scrapy engine headers, need have your own cookie   --- type:"dict"
    """
    # print(url)
    try:
        content = requests.get(url,headers = headers,timeout = 500)
        # print(content.content)
        json_file = content.content.decode('utf-8','ignore')
        # print(content)
        # print(json_file)
        json_file = json.loads(json_file)
        # print(json_file)
        time.sleep(0.5)
        return json_file
    except:
        """
        if error return None and print the url
        """
        print("Get" + url + " failed")
        return None




def get_search_web(keyword, page):
    """
    keyword: 搜索的关键词
    page: 搜索的页数
    根据关键词和搜索页数设置对应url, 并返回爬取的json文件
    """
    page = str(page)
    search_url = "https://m.weibo.cn/api/container/getIndex?type=all&queryVal=" + keyword  +  \
                    "&featurecode=20000320&luicode=10000011&lfid=106003type%3D1&title=" + keyword + \
                    "&containerid=100103type%3D1%26q%3D" + keyword  + "&page=" + page   +  "&display=0&retcode=6102&#39;"

    return get_info(search_url, utils.headers)




def decode_search_info(json_file):
    """
    解析json 文件
    """
    blogs = []
    blog = {}
    if json_file == None:
        return None
    have_result = True
    print(json_file)
    try:
        # if(len(json_file['cards']) == 0):
        #     """
        #     没有结果返回空
        #     """
        #     return blogs
        if (len(json_file['data']['cardlistInfo']) == 0):
            """
            没有结果返回空
            """
            return blogs
    except Exception:
        print("it seems the json parse err")
    
    #result_num = json_file['cardlistInfo']['page']
    # if(result_num==None):
    #     have_result = False
    #     return None

    # print(json_file['data'].keys())

    if "cards" not in json_file['data'].keys():
        # 爬到的不是搜索结果  返回
        return blogs

    json_file = json_file['data']['cards']

    for i in json_file:
        print(i)

    # num = 0
    for i in json_file:
        # print("search_result",num)
        # num+=1
        if 'card_group' not in i:
            continue
        # if 'title' in i.keys():
        sub_blog = i['card_group']
            # print(sub_blog)
        for j in sub_blog:
            # print(j)
            if 'mblog' not in j.keys():
                continue
            blog = {}
            temp_blog = j['mblog']
            user = temp_blog['user']
            blog['created_at'] = temp_blog['created_at']
            if len(re.findall(utils.re_limited_time,blog['created_at'])) > 0:
                return blogs   #微博 搜索结果按时间顺序排序, 如果搜索出来时间早于 2015 那之后的也会早于了
            blog['bid'] = temp_blog['id']
            blog['reposts_count'] = temp_blog['reposts_count']
            blog['comments_count'] = temp_blog['comments_count']
            blog['uid'] = user['id']
            blog['url'] = j['scheme']
            blog['text'] = temp_blog['text']
            blog['user_followers_count'] = user['followers_count']
            # print(blog)
            # if()
            blogs.append(blog)
    print("######")
    print(blogs)
    print("######")
    return blogs

def get_search( keyword):
    """
    从第一页开始爬,如果返回搜索微博为0 停止
    """

    page = 1
    search_blog = []
    while(True):
        if(len(search_blog) > utils.limit / 2):
            break
        json_file = get_search_web(keyword,page)
        new_search_blog = decode_search_info(json_file)
        # print(new_search_blog)
        if len(new_search_blog) == 0:
            break
        else:
            search_blog.extend(new_search_blog)
        page+=1
    # json_file = get_search_web(keyword, headers)
    # if(json_file!=None):
    #     search_blog = decode_search_info(json_file)
    # else:
    #     return None
    if len(search_blog) == 0:
        print("Can not find any result with keywords: " + keyword)
        time.sleep(5)
        return None
    else:
        search_blog = pd.DataFrame(search_blog)
        # print(search_blog)
        search_blog.drop_duplicates(['bid'],inplace = True)
        search_blog.index = np.arange(len(search_blog))
        # search_blog.to_csv(rootdir + "search_blog_%s.csv"%(keyword),index=False,sep='\t')
        # print(search_blog)
        return search_blog








"""
user 相关函数为爬取用户个人信息
"""



def get_user_web(uid):
    """
    uid 为用户id, 设置对应url
    返回爬取的json 文件
    """
    uid = str(uid)
    user_url = "https://m.weibo.cn/api/container/getIndex?containerid=230283" + uid + \
        "_-_INFO&lfid=230283" + uid + "&display=0&retcode=6102&#39";
    json_file = get_info(user_url,headers = utils.headers)
    return json_file


def decode_user_info(json_file):
    """
    解析json 文件
    """

    info_list = ['昵称','注册时间','简介','性别', '年龄','所在地','微信号','is_V','v_简介','标签','教育经历']   # 需要获取的数据
    info_dict = {}
    for i in info_list:
        info_dict[i] = ''
    if json_file == None:
        return info_dict
    a = json_file['data']['cards']
    info_dict['is_V'] = '0'
    for i in a:
        print(i.keys())
        if 'card_group' in i.keys():
            sub_description = i['card_group']
            print("********")
            print(sub_description)
            for j in sub_description:
                if('item_type' in j.keys() and j['item_type'] == 'verify_yellow'):
                    info_dict['is_V'] = '1'   #大V标志的格式在json文件中与其他不同
                    info_dict['v_简介'] = j['item_content']
                if 'item_name' in j.keys():
                    for info in info_list:
                        if j['item_name'] == info:
                            info_dict[info] = j['item_content']
    return info_dict

def get_basic_user_web(uid):
    uid = str(uid)
    user_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value=" + uid + \
    "&containerid=100505" + uid
    try:
        content = requests.get(user_url,utils.headers)
        content = content.content.decode('utf-8','ignore')
        return content
    except:
        print("get %s user's basic info failed"%(uid))
        return None


def get_user_basic_info(uid):
    user_info = {}
    keywords = ['follow_count','followers_count']
    for i in keywords:
        user_info[i] = ''
    content = get_basic_user_web(uid)
    if content == None:
        return
    else:
        for i in keywords:
            re_precompile = '"' + i + '":([0-9]+),'
            re_keyword = re.compile(re_precompile)
            result = re.findall(re_keyword,content)
            if len(result) >0:
                user_info[i] = result[0]
        return user_info

#def get_user_info(uid):
#    """
#    获取单个用户的信息
#    """
#    user_url = "https://m.weibo.cn/u/"+str(uid)   # 加一个用户主页的网址
#    # try:
#    #     requests.get(usr_url)
#    # except:
#    #     pass
#    json_file = get_user_web(uid)
#    user_dict = decode_user_info(json_file)
#    user_dict['uid'] = uid
#    user_dict['url'] = user_url
#    return user_dict

def get_user_info(uid):
    """
    获取单个用户的信息
    """
    # if(type(uid)==str)
    user_url = "https://m.weibo.cn/u/"+str(uid)   # 加一个用户主页的网址
    # try:
    #     requests.get(usr_url)
    # except:
    #     pass
    user_basic_info = get_user_basic_info(uid)
    json_file = get_user_web(uid)
    print("$$$$$$$")
    print(type(json_file))
    print(json_file)
    print("$$$$$$$")
    user_dict = decode_user_info(json_file)
    user_dict['uid'] = uid
    user_dict['url'] = user_url
    for i in user_basic_info.keys():
        user_dict[i] = user_basic_info[i]
    return user_dict

def get_user_infos(uid_list):
    """
    获取多个用户的信息
    """

    uid_list = set(uid_list)
    user_infos = []
    for i in uid_list:
        user_infos.append(get_user_info(i))
    return pd.DataFrame(user_infos)

"""
follower 相关函数为爬取单个用户的关注人
并按是否是大V以及粉丝数量排序,最后输出一个 DataFrame 矩阵
"""


def get_follower_web(uid,page):
    """
    根据 uid 和页数设置url 返回json数据
    """
    uid = str(uid)
    page = str(page)
    follwer_url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_" + uid + \
                    "&luicode=10000011&lfid=100505" + uid + \
                    "&featurecode=20000320&page=" + page + "&display=0&retcode=6102&#39;"
    return get_info(follwer_url,utils.headers)


def decode_follower_info(uid,json_file):
    """
    解析json 数据 爬取 关注人的:uid, 个人描述 , 昵称, 是否是大V, 大V认证原因, 粉丝数量
    """
    followers = []
    if  (json_file is None) or "cards" not in json_file.keys():
        return followers
    json_file = json_file['data']['cards']
    if(len(json_file) > 0):
        a = json_file[0]
        for i in a['card_group']:
            follower = {}
            follower['followed_uid'] = uid
            follower['follower_uid'] = i['user']['id']
            follower['description'] = i['user']['description']
            follower['name'] = i['user']['screen_name']
            if(i['user']['verified'] == True):
                follower['is_V'] = 1
                if 'verified_reason' in i['user'].keys():
                    follower['v_description'] = i['user']['verified_reason']
            else:
                follower['is_V'] = 0
                follower['v_description'] = ''
            follower['followers_count'] = i['user']['followers_count']
            followers.append(follower)
    return followers

def get_follower_info(rootdir, uid):
    """
    爬取单个uid的关注者信息, 但因为关注者第一页跟第二页及以后返回的json数据不同,因此第一页单独分析
    并保存到每个uid 的文件夹中
    """
    headers = utils.headers
    uid = str(uid)
    followers = []
    page = 1
    json_file = get_follower_web(uid,page)
    json_file = json_file['data']['cards']
    for i in json_file:
        # print(i)
        if 'title' in i.keys() and i['title'][-4:] =="全部关注":
            for j in i['card_group']:
                follower = {}
                follower['followed_uid'] = uid
                follower['follower_uid'] = j['user']['id']
                follower['description'] = j['user']['description']
                follower['name'] = j['user']['screen_name']
                if(j['user']['verified'] == True):
                    follower['is_V'] = 1
                    if 'verified_reason' in j['user'].keys():
                        follower['v_description'] = j['user']['verified_reason']
                    else:
                        follower['is_V'] = 0
                        follower['v_description'] = ''
                follower['followers_count'] = j['user']['followers_count']
                followers.append(follower)
    if(len(followers)) == 0:
        return None

    #第二页的内容有
    page = 3
    while(True):
        json_file = get_follower_web(uid,page)
        # print(json_file)
        new_follower = decode_follower_info(uid,json_file)
        if(len(new_follower)==0):
            break
        else:
            followers.extend(new_follower)
        page+=1
    followers = pd.DataFrame(followers)
    if not os.path.exists(rootdir + "uid_"+uid) :
        os.mkdir(rootdir + "uid_"+uid)
    columns = ['followed_uid','follower_uid','description','name','is_V','v_description','followers_count']
    followers = followers.reindex(columns=columns)
    followers = followers[columns]
    # followers = followers[['followed_uid','follower_uid','description','name','is_V','v_description','followers_count']]
#    folloers = followers.sort_values(by=['is_V','followers_count'],ascending=False)
    followers.to_csv(rootdir + "uid_"+str(uid)+"/followers.csv",sep='\t',index=False)
    return followers

def get_followers_info(rootdir,uid_list):
    print("Begin scrapy followers info")
    uid_list = set(uid_list)
    for i in uid_list:
        followers = get_follower_info(rootdir, i)
        time.sleep(1)
    return None



def get_blog_web(uid,page):
    """
    uid : 用户id
    设置获取这个人 第 page 页微博的json数据
    """
    uid = str(uid)
    page = str(page)
    blog_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value=" + uid + \
                "&containerid=107603" + uid

    if(int(page)>1):
        blog_url = blog_url + "&page=" + page
    blog_url +="&display=0&retcode=6102&#39;"
    return get_info(blog_url,utils.headers)



def decode_blog_info(uid,json_file):
    """
    解析json 数据
    """
    blogs = []
    if(json_file == None):
        return blogs
    json_file = json_file['data']['cards']
    if(len(json_file)==0):
        return blogs
    for i in json_file:
        if "mblog" not in i.keys():
            continue

        blog = {}
        blog['uid'] = uid
        blog['blog_url'] = i['scheme']
        mblog = i['mblog']
        blog['created_at'] = mblog['created_at']
        if len(re.findall(utils.re_limited_time, blog['created_at'])) > 0:
            continue
        if 'raw_text' in mblog.keys():
            blog['text'] = mblog['raw_text']
        else:
            blog['text'] = mblog['text']
        blog['mid'] = mblog['mid']
        blog['reposts_count'] = mblog['reposts_count']
        blog['comments_count'] = mblog['comments_count']
        if 'source' in mblog.keys():
            blog['source'] = mblog['source']
        else:
            blog['source'] = ''

        if 'retweeted_status' in mblog.keys():
            blog['retweeted_mid'] = str(mblog['retweeted_status']['id'])
            if 'raw_text' in mblog['retweeted_status'].keys():
                blog['retweeted_text'] = mblog['retweeted_status']['raw_text']
            else:
                blog['retweeted_text'] = mblog['retweeted_status']['text']
            if mblog['retweeted_status']['user'] != None:
                blog['retweeted_name'] = mblog['retweeted_status']['user']['screen_name']
                blog['retweeted_uid'] = str(mblog['retweeted_status']['user']['id'])
                blog['retweeted_profile_url'] = mblog['retweeted_status']['user']['profile_url']
            else:
                blog['retweeted_name'] = ''
                blog['retweeted_uid'] = ''
                blog['retweeted_profile_url'] = ''

        else:
            blog['retweeted_mid'] = ''
            blog['retweeted_name'] = ''
            blog['retweeted_profile_url'] = ''
            blog['retweeted_text'] = ''
            blog['retweeted_uid'] = ''
        blog['text'] = blog['text'] + blog['retweeted_text']

        blogs.append(blog)

    return blogs


def get_blog_info(rootdir, uid):
    """
    获取一个人的微博
    从第一个开始循环,到返回空时结束
    """
    # int current_limit = 0
    headers = utils.headers
    print("Begin scrapy uid %s's blog information"%(str(uid)))
    start_time = time.time()
    blogs = []
    page = 1
    while(True):
        if(len(blogs) > utils.limit):
            break
        json_file = get_blog_web(uid,page)
        new_blog = decode_blog_info(uid,json_file)
        if(len(new_blog)==0):
            break
        blogs.extend(new_blog)
        page+=1
        time.sleep(1)
    #保存
    blogs= pd.DataFrame(blogs)
    blogs.to_csv(rootdir + "uid_"+str(uid)+"/blog.csv",sep = '\001',index = False)

    # get_reposts_info(uid,blogs['mid'].values,blogs['reposts_count'].values,headers)
    print("Finish scrapy uid %s's blog information,using time:%d"%(str(uid),time.time() - start_time))

    return blogs


def get_blogs_info(rootdir, uid_list):
    """
    获取多个人信息
    """
    uid_list = set(uid_list)
    for uid in uid_list:
        blogs = get_blog_info(rootdir, uid)
        # time.sleep(1)
    time.sleep(10)
    return None


def get_repost_web(bid,page):
    bid = str(bid)
    page = str(page)
    reposts_url = "https://m.weibo.cn/api/statuses/repostTimeline?id=" + bid + \
                "&page=" + page + "&display=0&retcode=6102&#39;"
    return get_info(reposts_url,utils.headers)


def decode_reposts_info(bid,json_file):
    """
    解析转发的json文件
    """
    reposts = []
    if(json_file == None):
        return reposts
    if('data' not in json_file.keys()):
        print(json_file)
        return reposts
    json_file = json_file['data']['data']
    if(len(json_file) == 0):
        return reposts
    for i in json_file:
        repost = {}
        repost['bid'] = bid
        repost['created_at'] = i['created_at']
        # if(re.findal)
        repost['repost_id'] = i['id']
        repost['uid'] = i['user']['id']
        repost['user_name'] = i['user']['screen_name']
        # if 'raw_text' in i.keys():
        #     repost['text'] = i['raw_text']
        # else:
        #     repost['text'] = i['text']
        reposts.append(repost)
    return reposts


def get_repost_info(bid):
    """
    获取一条微博的转发
    """
    page = 1
    reposts = []
    while(True):
        if(len(reposts) > utils.limit):
            break
        json_file = get_repost_web(bid,page)
        new_repost = decode_reposts_info(bid,json_file)
        if len(new_repost)==0:
            break
        else:
            reposts.extend(new_repost)
        page+=1
    return reposts


def get_reposts_info(rootdir,uid,bid_list,reposts_count):
    """
    获取多条微博的转发,
    bid_list存微博的数目 type 为 DataFrame
    reposts_count为 每条微博的转发数目,等于0 则不获取
    """
    reposts = []
    for idx in bid_list.index:
        bid = bid_list.ix[idx,'bid']
        if(reposts_count[idx]==0):
            continue
        reposts.extend(get_repost_info(bid))
        # time.sleep(5)
    reposts = pd.DataFrame(reposts)
    if(len(bid_list) == 1):
        bid = bid_list.ix[bid_list.index[0],'bid']
        reposts.to_csv(rootdir + "uid_"+str(uid)+"/blog_reposts_bid_" + bid + ".csv",sep='\001',index=False)
    else:
        reposts.to_csv(rootdir + "uid_"+str(uid)+"/blog_reposts.csv",sep='\001',index=False)
    return None



def get_comment_web(bid, page):
    bid = str(bid)
    page = str(page)
    comments_url = "https://m.weibo.cn/api/comments/show?id=" + bid + \
                "&page=" + page + "&display=0&retcode=6102&#39;"

    return get_info(comments_url,utils.headers)

def decode_comments_info(bid,json_file):
    comments = []
    if(json_file == None):
        return comments
    if('data' not in json_file.keys()):
        print(json_file)
        return comments

    json_file = json_file['data']['data']
    if(len(json_file) == 0):
        return comments
    for i in json_file:
        comment = {}
        comment['bid'] = bid
        comment['created_at'] = i['created_at']
        # if len(re.findall(utils.re_limited_time,comment['created_at'])) > 0:
        #     continue
        comment['comment_id'] = i['id']
        comment['uid'] = i['user']['id']
        # comment['user_name'] = i['user']['name']
        if 'raw_text' in i.keys():
            comment['text'] = i['raw_text']
        else:
            comment['text'] = i['text']
        comments.append(comment)
    return comments


def get_comment_info(bid):
    page = 1
    comments = []
    while(True):
        if(len(comments) > utils.limit):
            break
        json_file = get_comment_web(bid,page)
        # print(json_file)
        new_comment = decode_comments_info(bid, json_file)
        if len(new_comment) == 0:
            break
        else:
            comments.extend(new_comment)
        page+=1
    return comments

def get_comments_info(rootdir, uid, bid_list, comments_count):
    comments = []
    for idx in bid_list.index:
        bid = bid_list.ix[idx,'bid']
        if(comments_count[idx] == 0):
            continue
        comments.extend(get_comment_info(bid))
    comments = pd.DataFrame(comments)
    # comments = pd.DataFrame(comments)
    if(len(bid_list) == 1):
        bid = bid_list.ix[bid_list.index[0]]
        comments.to_csv(rootdir + "uid_"+str(uid) + "/blog_comments_bid_" + bid + ".csv", sep='\001',index = False)
    else:
        comments.to_csv(rootdir + "uid_"+str(uid) + "/blog_comments.csv", sep='\001',index = False)
    return None
#
#
# keyword = 'dota2'
# m_search_url = 'https://m.weibo.cn/p/100103type%3D1%26q%3D'+ keyword
# d_search_url = 'http://s.weibo.com/weibo/' + keyword
#
# d_cookie = "_T_WM=10483ee0dc45c38eed523efea888bcae; H5:PWA:UID=1; ALF=1512751689; SCF=AquP96Utlp8YRk0uJg95bFJR8SJ9aD6FoZYo5G3aWBtE76bEuYz6KD8yvs84d339oXsnYaPCNzjJM_e-lc7TRrU.; SUB=_2A253B0UZDeRhGeRO4lEV9ivFzTuIHXVUCGtRrDV6PUNbktBeLVHlkW1yskNAd1Ph_quSL3tNA-6paFk2yg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W50YwhuMpEHsRAAY_PboMLz5JpX5KMhUgL.Foz71KeXSo-4SoM2dJLoI7ye9PxQ9CfjMBtt; SUHB=0h14i9PwyyAP7a; SSOLoginState=1510159689; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D2302831845178932%26featurecode%3D20000320%26fid%3D23028313932_-_INFO%26uicode%3D10000011"
#
#
# # print(content.content)
# #
# # user_id = '5227594010'
# # url = 'http://weibo.cn/u/%d?filter=1&page=1'%user_id
# #
if __name__=="__main__":
    # scrapy_info('xiangya')
    scrapy_info('卢本伟')
    # jsonfile = dict({'ok': 1, 'data': {'cardlistInfo': {'v_p': '42', 'cardlist_title': '', 'desc': '', 'show_style': 1, 'can_shared': 0, 'containerid': '2302835652760087_-_INFO', 'cardlist_menus': [{'type': 'button_menus_refresh', 'name': '刷新'}, {'type': 'gohome', 'name': '返回首页', 'params': {'scheme': 'sinaweibo://gotohome'}}], 'page': None}, 'cards': [{'card_type': 11, 'card_group': [{'card_type': 42, 'display_arrow': 0, 'desc': '账号信息'}, {'card_type': 41, 'item_name': '昵称', 'item_content': '简图图是誰'}, {'card_type': 41, 'item_name': '简介', 'item_content': '佛系fans'}]}, {'card_type': 11, 'card_group': [{'card_type': 42, 'display_arrow': 0, 'desc': '个人信息'}, {'card_type': 41, 'item_name': '性别', 'item_content': '男'}, {'card_type': 41, 'item_name': '所在地', 'item_content': '江苏'}]}], 'showAppTips': 0, 'scheme': 'sinaweibo://cardlist?containerid=2302835652760087_-_INFO&extparam=&luicode=10000011&lfid=2302835652760087&featurecode=20000320&from=1110006030'}})
    # jsonfile2 = dict({{'card_type': 42, 'display_arrow': 0, 'desc': '账号信息'}, {'card_type': 41, 'item_name': '昵称', 'item_content': '霄轲珂珂'}, {'card_type': 41, 'display_arrow': 1, 'itemid': '2302835436452354_-_WEIBO_INDEX_PROFILE_VERFIED_CARD', 'item_type': 'verify_yellow', 'item_content': '游戏博主', 'scheme': 'http://verified.weibo.com/verify?luicode=10000011&lfid=2302835436452354_-_INFO&featurecode=20000320', 'actionlog': {'act_code': '594', 'uicode': '10000198', 'oid': '2302835436452354_-_INFO', 'fid': '2302835436452354_-_INFO', 'cardid': '230283_-_WEIBO_INDEX_PROFILE_VERFIED_CARD', 'ext': 'uid:|ouid:5436452354|verified_type:0|ptype:0|load_read_level:2'}}, {'card_type': 41, 'item_name': '简介', 'item_content': 'bilibili 霄轲x'}})
    # decode_user_info(jsonfile2)