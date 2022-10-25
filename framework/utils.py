import re


def convert_url_to_regex(url: str):
    new_url_list = []
    for word in url.split("/"):
        if re.match("^<int:.+>", word):
            group_name = word.replace("<int:", "")[:-1]
            new_url_list.append(f"(?P<{group_name}>[0-9]+)")
            continue
        if re.match('^<.+>$', word):
            group_name = word[1:-1]
            new_url_list.append(f"(?P<{group_name}>.+)")
            continue

        new_url_list.append(re.escape(word))
    regexpattern = "/".join(new_url_list)
    return f'^{regexpattern}$'
