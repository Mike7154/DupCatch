import re
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from pattern.text.en import singularize


def combine_remove_common(field1, field2, pattern):
    matching = find_text(field2, pattern)
    new_string_2 = field2
    for m in matching:
        if m in field1:
            new_string_2 = re.sub(m, '', new_string_2)
    return clean_ws(new_string_2)


def download_wordnet():
    nltk.download('verbnet3')
    nltk.download('popular')


def singulize(words):
    return [singularize(w) for w in words]


def lemm_sing(words):
    ls = word_lemmatizer(words)
    return singulize(ls)


def word_lemmatizer(words):
    return [WordNetLemmatizer().lemmatize(w, 'v') for w in words]


def clean_text(str, pattern, replacement=" "):
    # basic html cleaner CLEANR = re.compile('<.*?>')
    # full HTML cleaner CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(pattern, replacement, str)
    return cleantext


def clean_patterns(input_text, patterns, replacement=""):
    cleantext = input_text
    for p in patterns:
        cleantext = re.sub(p, replacement, cleantext)
    return cleantext


def clean_patterns_words(str_list, pattern_list, replacement=""):
    out_words = []
    for w in str_list:
        cleanword = clean_patterns(w, pattern_list, replacement)
        out_words.append(cleanword)
    return out_words


def get_tag_string(str, tag='b'):
    reg_str = "<" + tag + "[^>]*>(.*?)</" + tag + ">"
    res = re.findall(reg_str, str)
    return res


def compile_html_cleaner(extensive=True):
    if extensive:
        return re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    else:
        return re.compile('<.*?>')


def compile_html_tag(tag='b'):
    pattern = "<" + tag + "[^>]*>(.*?)</" + tag + ">"
    return re.compile(pattern)


def find_text(str, pattern):
    # re.compile('\{\{c[0-9]+::(.*?)[/}:]{2}')
    res = re.findall(pattern, str)
    return res


def clean_ws(text_to_clean):
    cleaned = re.sub(" +", " ", text_to_clean)
    return cleaned.strip()


def split_list(str_list, sep=" "):
    out = []
    for str in str_list:
        ctext = clean_ws(str)
        if ctext == '':
            continue
        else:
            sub_split = ctext.split(sep)
            out.extend(sub_split)
    return out


def unicode_dict():
    return {'â†”': '↔', "â†‘": "↑", "â†“": "↓", "Î²": "β", "Î±": "α", "ÃŽÂ²": "Î²", "ÃŽÂ±": "Î±"}


def replace_words(words, word_dict):
    out_words = []
    for w in words:
        new_word = word_dict.get(w)
        if new_word is None:
            out_words.append(w)
        else:
            out_words.append(new_word)
    return out_words


def replace_patterns(str, synonym_dict):
    new_string = str
    for key in synonym_dict:
        pattern = '(?<![a-zA-Z])' + key + '(?![a-zA-Z])'
        replacement = synonym_dict.get(key)
        new_string = re.sub(pattern, replacement, new_string, flags=re.IGNORECASE)
    return new_string


def reverse_synonym_dict(synonym_dict, replace_dict):
    new_dict = {}
    for key in synonym_dict.keys():
        words = synonym_dict.get(key)
        words = replace_words(words, replace_dict)
        for w in words:
            new_dict.update({w: key})
    return new_dict


def clean_words(words, pattern='[^A-Za-z0-9]+'):
    out = []
    for w in words:
        str = re.sub(pattern, '', w)
        str = str.lower()
        if len(str) > 0:
            out.append(str)
    return out


def have_common(word_list1, word_list2):
    common = False
    for w in word_list1:
        if w in word_list2:
            common = True
    return common
