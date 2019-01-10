import csv


def get_keywords(file_path):
    """
    get keywords list from file_path
    :param file_path: the keywords list file's path
    :return: keywords in a list
    """
    with open(file_path) as keyword_file:
        keywords = keyword_file.read().split("\n")
    return keywords


def save_to_csv(file_path, headers, data):
    with open(file_path, "w") as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(data)
    return True
