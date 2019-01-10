import requests
import logging
import json
import time
import utils
import re


class Spider(object):
    """
    base spider class
    """

    def __init__(self):
        pass


class WeiboSpider(Spider):
    """
    used to get some information from weibo with keywords
    1. use cookies to login
    2. use weibo's search engine to find data with keywords
    3. get the users' information in the search results

    TODO: add multi-threads supports
    """

    search_url = "https://m.weibo.cn/api/container/getIndex?type=all&queryVal={keyword}" \
                 "&featurecode=20000320&luicode=10000011&lfid=106003type%3D1&title={keyword}" \
                 "&containerid=100103type%3D1%26q%3D{keyword}&page={page}&display=0&retcode=6102&#39;"
    cookie = ""
    max_page = 5
    headers = dict()
    results = list()
    timeout = 500
    keyword = ""
    users = list()
    users_results = list()

    def __init__(self, cookie, user_agent, max_page):
        super().__init__()
        self.cookie = cookie
        self.max_page = int(max_page)
        self.headers = {"User-Agent": user_agent,
                        "cookie": cookie}

    def catch_keyword(self, keyword):
        """
        catch search results data with keyword
        :param keyword: string, the keyword
        :return: list, the results
        """
        logging.info("Start to catch keyword [%s]" % keyword)
        self.keyword = keyword
        self.results = list()
        self.users = list()
        # get results of the keywords
        for page in range(0, self.max_page):
            temp_result = self.catch_page(keyword, page)
            self.results.extend(temp_result)
            self.users.extend([item['uid'] for item in temp_result])
            logging.info("caught page %s" % page)
            time.sleep(2)
        # get rid of same users, this method is not good
        # TODO: use a more efficient method
        self.users = list(set(self.users))
        # get results of users in the search results
        self.users_results = list()
        for user in self.users:
            self.users_results.append(self.catch_user(user))
            time.sleep(1)

        self.save(self.results, self.users_results)
        return self.results

    def catch_page(self, keyword, page):
        """
        catch the page's data
        :param keyword: string, the keyword
        :param page: int, the page id
        :return: list, the page's data
        """
        content = str()
        try:
            content = requests.get(url=self.search_url.format(keyword=keyword, page=page),
                                   headers=self.headers, timeout=self.timeout).content.decode("utf-8", "ignore")
        except Exception as e:
            logging.error("error occurred while catch page %s of keyword %s" % (page, keyword))
            return list()
        return self.parse_page_results(json.loads(content))

    def parse_page_results(self, data):
        """
        parse the page results
        :param data: data after json loading
        :return: parsed data
        """
        posts = list()
        if len(data['data']['cardlistInfo']) == 0 or "cards" not in data['data'].keys():
            # return empty
            return posts

        posts_data = data['data']['cards']

        for card in posts_data:
            if "card_group" not in card:
                continue
            sub_group = card["card_group"]
            for item in sub_group:
                if "mblog" not in item.keys():
                    continue
                temp_data = item["mblog"]
                # TODO: add time limited

                item_data = dict(
                    created_at=temp_data["created_at"],
                    bid=temp_data["id"],
                    reposts_count=temp_data["reposts_count"],
                    comments_count=temp_data["comments_count"],
                    uid=temp_data["user"]["id"],
                    url=item["scheme"],
                    text=temp_data["text"],
                    user_followers_count=temp_data["user"]["followers_count"]
                                 )
                posts.append(item_data)
        logging.debug(posts)
        return posts

    def catch_user(self, uid):
        """
        get information of the user identified by uid
        :param uid: string, user's uid
        :return: dict, data of the user
        """
        logging.info("start to catch user [%s]'s info" % uid)
        user_url = "https://m.weibo.cn/u/" + str(uid)
        user_data = dict()

        user_data["uid"] = uid
        user_data["url"] = user_url

        # get follow count and followers count
        follow_data_url = "https://m.weibo.cn/api/container/getIndex" \
                          "?type=uid&value={uid}&containerid=100505{uid}".format(uid=uid)
        follow_content = requests.get(url=follow_data_url,
                                      headers=self.headers,
                                      timeout=self.timeout).content.decode("utf-8", "ignore")
        print(follow_content)
        follow_keyword_list = ["follow_count", "followers_count"]
        for item in follow_keyword_list:
            temp_re = re.compile('"{key}":([0-9]+),'.format(key=item))
            result = re.findall(temp_re, follow_content)
            if len(result) > 0:
                user_data[item] = result[0]

        # get user's detail information
        detail_url = "https://m.weibo.cn/api/container/getIndex?containerid=230283{uid}_-_INFO&" \
                     "lfid=230283{uid}&display=0&retcode=6102&#39".format(uid=uid)

        detail_content = requests.get(url=detail_url,
                                      headers=self.headers,
                                      timeout=self.timeout).content.decode("utf-8", "ignore")
        detail_json = json.loads(detail_content)
        detail_headers = ['昵称', '注册时间', '简介', '性别', '年龄', '所在地', '微信号', 'is_V', 'v_简介', '标签', '教育经历']
        detail_card = detail_json["data"]["cards"]
        user_data["is_V"] = '0'
        for item in detail_card:
            if 'card_group' in item.keys():
                sub_description = item["card_group"]
                for item_ in sub_description:

                    # 大V标志的格式在json文件中与其他不同
                    if "item_type" in item_.keys() and item_["item_type"] == "verify_yellow":
                        user_data["is_V"] = '1'
                        user_data["v_简介"] = item_["item_content"]
                    if "item_name" in item_.keys():
                        for info in detail_headers:
                            if item_["item_name"] == info:
                                user_data[info] = item_["item_content"]

        return user_data

    def save(self, search_results, user_results):
        """
        save data to file
        :return: True if success or False
        """
        search_results_headers = ["bid", "comments_count", "created_at", "reposts_count", "text", "uid", "url",
                                  "user_followers_count"]
        utils.save_to_csv("data/"+self.keyword+"_posts.csv", search_results_headers, search_results)

        user_results_headers = ["follow_count", "followers_count", "is_V", "uid", "url", "v_简介", "年龄", "微信号",
                                "性别", "所在地", "教育经历", "昵称", "标签", "注册时间", "简介", "blog_dir", "follower_dir"]
        utils.save_to_csv("data/"+self.keyword+"_users.csv", user_results_headers, user_results)
        return True
