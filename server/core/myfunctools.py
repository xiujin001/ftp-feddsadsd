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


def create_file_md5(file_path):
    md = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            f_part = f.read(8196)
            if not f_part:
                break
            md.update(f_part)
    return md.hexdigest()


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
    file_path = settings.USER_FILE % account
    for rootdir, dirs, filenames in os.walk(file_path):
        file_size += sum([os.path.getsize(os.path.join(rootdir, file)) for file in filenames])
    return file_size


def get_dir_size(file_path):
    file_size = 0
    for rootdir, dirs, filenames in os.walk(file_path):
        file_size += sum([os.path.getsize(os.path.join(rootdir, file)) for file in filenames])
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
    return "total quota: %s bytes\nused quota: %s bytes\nquota left: %.2f%%" % \
           (total_quota, used_quota, (total_quota - used_quota) / total_quota * 100)


def is_file_complete(file):
    pass


def create_dir(user_file, file_path_list):
    create_dir_name = user_file
    for file_path in file_path_list:
        create_dir_name = os.path.join(create_dir_name, file_path)
    if os.path.exists(create_dir_name):
        return "this directory has already existed"
    else:
        os.makedirs(create_dir_name)
        return "create successfully"


def delete_all_file(del_file_path):
    print("remove_dir")
    file_list = os.listdir(del_file_path)
    for file in file_list:
        file_path = os.path.join(del_file_path, file)
        if os.path.isdir(file_path):
            delete_all_file(file_path)
        else:
            os.remove(file_path)
    # os.remove(del_file_path)
    os.system("rd/s/q %s" % del_file_path)
    print("removd_dir")


def remove_dir(user_file, file_path_list):
    print("remove_dir_entrace")
    remove_dir_name = user_file
    for file_path in file_path_list:
        remove_dir_name = os.path.join(remove_dir_name, file_path)
    if os.path.exists(remove_dir_name):
        delete_all_file(remove_dir_name)
        print("remove_dir_successfully")
        return "successfully removed"
    else:
        print("remove_dir_failed")
        return "directory or file doesn't exist"


def turn_to_dir(user_file, file_path_list, account):
    if len(file_path_list) == 1 and file_path_list[0] == "home":
        return 1, "you get back to home directory", settings.USER_FILE % account
    new_dir_name = user_file
    for file_path in file_path_list:
        new_dir_name = os.path.join(new_dir_name, file_path)
    if not os.path.isdir(new_dir_name):
        return 0, "this directory doesn't exist", None
    else:
        return 1, "you get into the new directory", new_dir_name


def print_directory_old(file_path):
    with open(settings.PRINT_FILE, "w") as f:
        for i, j, k in os.walk(file_path):
            p = os.path.basename(i)
            f.write(("----%s\n" % p))
            for jr in j:
                f.write("------%s\n" % jr)
            for ji in k:
                f.write("--------%s\n" % ji)
    with open(settings.PRINT_FILE, "r") as f:
        print(f.read())


def print_directory(file_path):
    with open(settings.PRINT_FILE, "w") as f:
        for rootdir, subdirs, files in os.walk(file_path):
            p = os.path.basename(rootdir)
            f.write(("----%s\n" % p))
            for subdir in subdirs:
                f.write("------dir:%s\n" % subdir)
            for ji in files:
                whole_name = os.path.join(rootdir, ji)
                file_size = os.path.getsize(whole_name)
                f.write("--------file:%s        %s bytes\n" % (ji, file_size))
        f.write("total :%s bytes" % get_dir_size(file_path))
