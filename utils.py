

def get_keywords(file_path):
    """
    get keywords list from file_path
    :param file_path: the keywords list file's path
    :return: keywords in a list
    """
    print(file_path)
    with open(file_path) as keyword_file:
        keywords = keyword_file.read().split("\n")
    return keywords
