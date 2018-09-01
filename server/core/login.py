# _*_ coding=utf-8_*_

from core import myfunctools


def login(user_account, user_password):
    """"用户登录验证模块"""
    if not myfunctools.check_account_exist(user_account):
        return 0, "Wrong account or password,please try again."

    if myfunctools.compare_pwd(user_account, user_password):
        user_status = myfunctools.get_account_option(user_account, "is_locked")
        if user_status == "1":
            return 0, "This account is locked for input errors beyond 3 times. "

        else:
            myfunctools.set_config_option(user_account, "wrong_input", "0")
            return 1, "Login successfully,welcome."

    else:
        wrong_input = int(myfunctools.get_account_option(user_account, "wrong_input")) + 1
        myfunctools.set_config_option(user_account, "wrong_input", str(wrong_input))
        if wrong_input == 3:
            myfunctools.set_config_option(user_account, "is_locked", "1")
        return 0, "Wrong account or password,please try again."
