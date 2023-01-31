import re


def get_group(path: str):
    return re.search('(?<=groups\/).+?(?=\/)', path).group()
