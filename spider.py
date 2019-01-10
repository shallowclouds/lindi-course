import requests
import logging
import json
import time


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
        self.results = list()
        for page in range(0, self.max_page):
            self.results.append(self.catch_page(keyword, page))
            logging.info("caught page %s" % page)
            time.sleep(2)
        self.save()
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
                item_data = dict()
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

    def save(self):
        """
        save data to file
        :return: True if success or False
        """
        pass
