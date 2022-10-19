import ruamel.yaml
import json
import urllib.parse
from datetime import datetime
import os
import glob
import  tkinter as tk
from tkinter import filedialog

def load_dict(file):
    f = open(file)
    url_dict = json.load(f)
    f.close()
    return url_dict


def write_dict(file, dict):
    with open(file, "w") as convert_file:
        convert_file.write(json.dumps(dict))

def create_json(json_file):
    if os.path.isfile(json_file) == False:
        dict = {}
        write_dict(json_file, dict)
def print_log(text):
    now = datetime.now()
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = timestr + " : " + text
    print(log_text)


def update_log(text):
    now = datetime.now()
    file = "logs.txt"
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = timestr + " : " + text
    print(log_text)
    f = open(file, "a")
    f.write(log_text+'\n')
    f.close()

def load_setting(section, setting, settings_file = "settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.allow_unicode = True
    with open(settings_file, encoding="utf-8") as fp:
        data = yaml.load(fp)
    return data[section][setting]

def save_setting(section, setting, value, settings_file = "settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    data[section][setting] = value
    with open(settings, "w") as f:
        yaml.dump(data,f)

def load_all_settings(settings_file = "settings.yml"):
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        with open(settings_file) as fp:
            data = yaml.load(fp)
        return data

def save_all_settings(data, settings_file = "settings.yml"):
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        with open(settings_file, "w") as f:
            yaml.dump(data,f)

def get_current_dir(folder = ""):
    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    return CURR_DIR + folder

def find_file(folder, extension = ""):
    path = folder + "*" + extension
    root = tk.Tk()
    root.withdraw()
    files = glob.glob(path)
    if len(files) == 0:
        if extension == "":
            file = filedialog.askopenfilename()
        else:
            ftypes = [(extension, extension)]
            print("could not file a matching " + extension + " file. please select a *" + extension + " file")
            file = filedialog.askopenfilename(filetypes=ftypes, defaultextension=extension)
    if len(files) > 1:
        for f in files:
            m = "Multiple matching files found, do you want to use " + f + "? (y/n): "
            if input(m) == "y":
                return f
    else:
        return files[0]
