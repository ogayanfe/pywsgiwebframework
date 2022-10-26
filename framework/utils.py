from genericpath import isdir
import re
import os
from typing import Optional


def convert_url_to_regex(url: str):
    new_url_list = []
    for word in url.split("/"):
        if re.match("^<int:.+>$", word):
            group_name = word.replace("<int:", "")[:-1]
            new_url_list.append(f"(?P<int_{group_name}>[0-9]+)")
            continue
        if re.match("^<str:.+>$", word):
            group_name = word.replace("<str:", "")[:-1]
            new_url_list.append(f"(?P<str_{group_name}>.+)")
            continue
        if re.match("^<float:.+>$", word):
            group_name = word.replace("<float:", "")[:-1]
            new_url_list.append(
                f"(?P<float_{group_name}>\d+(?:\.\d*)?|\.\d+)")
            continue
        if re.match('^<.+>$', word):
            group_name = word[1:-1]
            new_url_list.append(f"(?P<str_{group_name}>.+)")
            continue

        new_url_list.append(re.escape(word))
    regexpattern = "/".join(new_url_list)
    return f'^{regexpattern}$'


def get_directory_file_paths(parent_path: str, output: Optional[list] = []) -> list:
    """
        Returns the path of all file in a parent directory
    """
    if not os.path.exists(parent_path):
        return output
    for path in os.listdir(parent_path):
        child_path = os.path.join(parent_path, path)
        if os.path.isdir(child_path):
            return get_directory_file_paths(child_path, output)
        output.append(child_path)
    return output
