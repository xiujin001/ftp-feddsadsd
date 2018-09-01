# _*_ coding=utf-8_*_

import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
DB_FILE = os.path.join(BASE_DIR, 'db', "accounts", "%s.json")
CONF_FILE = os.path.join(BASE_DIR, 'db', "config.ini")
PKL_FILE = os.path.join(BASE_DIR, 'db', "pkl", "%s", "%s.pkl")
LOG_FILE = os.path.join(BASE_DIR, 'log', "log_info.log")
MAKE_FILE = os.path.join(BASE_DIR, 'db', "%s")
USER_FILE = os.path.join(BASE_DIR, 'db', "filespace", "%s")
DLD_FILE = os.path.join(BASE_DIR, 'db', "files_for_user_download")
PRINT_FILE = os.path.join(BASE_DIR, 'db', "print_file.txt")
LOG_LEVEL = logging.INFO
# print(DB_FILE)
CREATE_ACCOUNT_WARM = "用户账号为其用户名称,默认密码为123."

CONF_QUOTA = "524288000"
