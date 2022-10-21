import glob
import json
import os
import shutil
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
import ruamel.yaml
import logging


def settings_file(settings_file='settings.yml', template='settings_template.yml'):
    settings_file = copy_file(template, settings_file)
    return settings_file


def copy_file(file, destination_file):
    if not os.path.isfile(destination_file):
        shutil.copy(file, destination_file)
    return destination_file


def load_dict(file):
    f = open(file)
    url_dict = json.load(f)
    f.close()
    return url_dict


def write_dict(file, dict):
    with open(file, "w") as convert_file:
        convert_file.write(json.dumps(dict))


def create_json(json_file):
    if not os.path.isfile(json_file):
        dict = {}
        write_dict(json_file, dict)


def print_log(text):
    now = datetime.now()
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = timestr + " : " + text
    print(log_text)


def update_log(text):
    now = datetime.now()
    file = "bin/logs.txt"
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = timestr + " : " + text
    print(log_text)
    f = open(file, "a")
    f.write(log_text + '\n')
    f.close()


def load_setting(section, setting, settings_file="settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    yaml.allow_unicode = True
    with open(settings_file, encoding="utf-8") as fp:
        data = yaml.load(fp)
    return data[section][setting]


def save_setting(section, setting, value, settings_file="settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    data[section][setting] = value
    with open(settings_file, "w") as f:
        yaml.dump(data, f)


def load_all_settings(settings_file="settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    return data


def save_all_settings(data, settings_file="settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file, "w") as f:
        yaml.dump(data, f)


def get_current_dir(folder=""):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return curr_dir + folder


def find_file(folder, extension=""):
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
    else:
        file = files[0]
    if len(files) > 1:
        for f in files:
            m = "Multiple matching files found, do you want to use " + f + "? (y/n): "
            if input(m) == "y":
                return f
    return file


def clear_folder(folder):
    shutil.rmtree(folder)
    os.mkdir(folder)


def log_exception(exception_variable):
    log_filename = 'bin/logs.txt'
    update_log("An Error has Occurred")
    if hasattr(exception_variable, 'message'):
        print(exception_variable.message)
    else:
        print(exception_variable)
    logging.basicConfig(filename=log_filename, level=logging.DEBUG)
    logging.error(exception_variable, exc_info=True)
