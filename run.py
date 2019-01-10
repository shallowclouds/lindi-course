#!/usr/bin/python3
import configparser
import logging
import sys
import time
from spider import WeiboSpider
import utils

config = configparser.ConfigParser()


def init_logging():
    """
    init the logging format
    :return: None
    """
    logger = logging.getLogger()
    log_file = sys.path[0] + "/log/" + time.strftime(
        "%Y%m%d%H%M%S",
        time.localtime()
    ) + ".log"
    level = "DEBUG"
    formatter = "[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s"
    fh = logging.FileHandler(log_file, encoding="utf-8")

    # Apply the rules and add stdout logger
    logging.basicConfig(level=level, format=formatter)
    fh.setFormatter(logging.Formatter(formatter))
    logger.addHandler(fh)


def load_config():
    """
    load config from config.ini
    :return: None
    """
    if not config.read("config.ini", encoding="utf-8"):
        print("config file not existing or file in wrong format")
        exit(0)


def main():
    # initialize
    load_config()
    init_logging()
    # cookie = config.get("login", "cookie")
    cookie = "_T_WM=10483ee0dc45c38eed523efea888bcae; " \
             "ALF=1512609560; " \
             "SCF=AquP96Utlp8YRk0uJg95bFJR8SJ9aD6FoZYo5G3aWBtE--R6WSHb4gr2i7C_3WXhuzZzQiEznJmboPTZHYfsVGo.; " \
             "SUB=_2A253BXxoDeRhGeRO4lEV9ivFzTuIHXVUBgQgrDV6PUJbktBeLWzAkW1Pc5hhPY3IL00riTnWkTkHXxfMew..; " \
             "SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W50YwhuMpEHsRAAY_" \
             "PboMLz5JpX5K-hUgL.Foz71KeXSo-4SoM2dJLoI7ye9PxQ9CfjMBtt; " \
             "SUHB=0xnzDYHdJqx3kN; SSOLoginState=1510018104; " \
             "H5:PWA:UID=1; " \
             "M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D106003type%25" \
             "3D1%26fid%3D100103type%253D1%2526q%253Ddota2%26uicode%3D10000011"
    max_page = config.get("spider", "max_page")
    user_agent = config.get("login", "user_agent")
    weibo = WeiboSpider(cookie, user_agent, max_page)
    keywords = utils.get_keywords(config.get("spider", "keywords_list"))
    print(keywords)
    for keyword in keywords:
        weibo.catch_keyword(keyword)
        weibo.save()


if __name__ == "__main__":
    main()
