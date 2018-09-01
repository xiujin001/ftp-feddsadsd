# _*_coding:utf-8_*_

import configparser
import hashlib
import os

from conf import settings


def create_account(account, password):
    cf = configparser.ConfigParser()
    cf.read(settings.CONF_FILE)

    if account in cf.sections():
        print("False:your account is the same as other user")
        return False
    cf.add_section(account)
    cf[account]["password"] = create_md5(password)
    cf[account]["wrong_input"] = "0"
    cf[account]["is_locked"] = "0"
    cf[account]["quota"] = settings.CONF_QUOTA
    with open(settings.CONF_FILE, "w") as f:
        cf.write(f)


def set_config_option(section, option, new_value):
    cf = configparser.ConfigParser()
    cf.read(settings.CONF_FILE)
    if section not in cf.sections():
        return False
    cf[section][option] = new_value
    with open(settings.CONF_FILE, "w") as f:
        cf.write(f)


def get_account_option(account, option):
    cf = configparser.ConfigParser()
    cf.read(settings.CONF_FILE)
    return cf[account][option]


def check_account_exist(account):
    cf = configparser.ConfigParser()
    cf.read(settings.CONF_FILE)
    if account in cf.sections():
        return True
    else:
        return False


def create_md5(obj):
    md = hashlib.md5()
    md.update(obj.encode("utf-8"))
    return md.hexdigest()


def compare_file(file1, file2):
    md1 = create_md5(file1)
    md2 = create_md5(file2)
    if md1 == md2:
        return True
    else:
        return False


def compare_pwd(account, pwd):
    md1 = create_md5(pwd)
    cf = configparser.ConfigParser()
    cf.read(settings.CONF_FILE)
    md2 = cf[account]["password"]

    if md1 == md2:
        return True
    else:
        return False


def create_file_space(account):
    os.mkdir(settings.MAKE_FILE % account)


def get_size(account):
    file_size = 0
    user_file = settings.USER_FILE % account
    for file in os.listdir(user_file):
        path_temp = os.path.join(user_file, file)
        if os.path.isdir(path_temp):
            get_size(account)
        else:
            file_size += os.path.getsize(path_temp)
    return file_size


def check_quota_enough(account, file_size):
    current_quota = get_size(account)
    total_quota = int(get_account_option(account, "quota"))
    if total_quota < file_size + current_quota:
        return False
    else:
        return True

def print_quota(account):
    used_quota = get_size(account)
    total_quota = int(get_account_option(account, "quota"))
    return "total quota: %s\tused quota: %s\tremainder quota: %s" % (total_quota,used_quota,total_quota-used_quota)


def is_file_complete(file):
    pass


def create_dir(user_file,file_path_list):
    create_dir_name = user_file
    for file_path in file_path_list:
        create_dir_name = os.path.join(create_dir_name, file_path)
    if os.path.exists(create_dir_name):
        return "this directory has already existed"
    else:
        os.makedirs(create_dir_name)
        return "create successfully"


def turn_to_dir(user_file, file_path_list):
    new_dir_name = user_file
    for file_path in file_path_list:
        new_dir_name = os.path.join(new_dir_name, file_path)
    if not os.path.exists(new_dir_name):
        return 0, "this directory doesn't exist", None
    else:
        return 1, "you get into the new directory", new_dir_name


# def print_directory(file_path):
#     for parent, dirnames, filenames in os.walk(file_path):
#         for filename in filenames:
#             print(filename)
#             file_object.write(filename + '\n')
#     file_object.close()
#     return
# def print_directory(file_path):
#     string = ""
#     tab_num = 0
#     for file in os.listdir(file_path):
#         path_temp = os.path.join(file_path, file)
#         if os.path.isdir(path_temp):
#             print_directory(path_temp)
#         else:
#             file_size = os.path.getsize(path_temp)
#             file_basename = os.path.basename(path_temp)
#             dir_basename = os.path.basename(file_path)
#             string += ("\t" * tab_num) + dir_basename + "\n" + ("\t" * (tab_num + 1)) + file_basename + " "+file_size
#             tab_num += 1
#     return string
# s =print_directory(settings.DLD_FILE)


# create_account("1", "1")

# set_config_option("1", "wrong_input", "2")
def print_directory(file_path):
    with open(settings.PRINT_FILE, "w") as f:
        for i, j, k in os.walk(file_path):
            p = os.path.basename(i)
            f.write(("%s\n" % p))
            for jr in j:
                f.write("\t%s\n" % jr)
            for ji in k:
                f.write("\t\t%s\n" % ji)
# print_directory(settings.BASE_DIR)