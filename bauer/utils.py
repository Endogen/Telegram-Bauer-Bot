def is_number(string):
    """ Also accepts '.' in the string. Function 'isnumeric()' doesn't """
    try:
        float(string)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(string)
        return True
    except (TypeError, ValueError):
        pass

    return False


def esc_md(text):
    import re

    rep = {"_": "\\_", "*": "\\*", "[": "\\[", "`": "\\`"}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))

    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


def comp(pattern):
    """ Returns a pre compiled Regex pattern to ignore case """
    import re
    return re.compile(pattern, re.IGNORECASE)


def is_bool(v):
    return v.lower() in ("yes", "true", "t", "1", "no", "false", "f", "0")


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def bool2str(b):
    """ Return 'Yes' for True and 'No' for False """
    return "Yes" if b else "No"


# TODO: Use that in 'rain' plugin
def split_msg(msg, max_len=None, split_char="\n", only_one=False):
    """ Restrict message length to max characters as defined by Telegram """
    if not max_len:
        import bauer.constants as con
        max_len = con.MAX_TG_MSG_LEN

    if only_one:
        return [msg[:max_len][:msg[:max_len].rfind(split_char)]]

    remaining = msg
    messages = list()
    while len(remaining) > max_len:
        split_at = remaining[:max_len].rfind(split_char)
        message = remaining[:max_len][:split_at]
        messages.append(message)
        remaining = remaining[len(message):]
    else:
        messages.append(remaining)

    return messages
