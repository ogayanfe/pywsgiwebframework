import re


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


if __name__ == "__name__":
    x = convert_url_to_regex("ayanfe/<float:name>/boy/")
    print(x)
    print(re.search(x, "ayanfe/4.3/boy/"))
