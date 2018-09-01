# _*_coding:utf-8_*_


import os
import sys
import json
import struct
from socket import *

from conf import settings
from core import login
from core import myfunctools


class Server:
    address_family = AF_INET
    socket_type = SOCK_STREAM
    # IP_port = ("127.0.0.1",6666)
    allow_reuse_address = True
    max_packet_size = 8192
    coding = "utf-8"
    request_queue_size = 5
    server_dir = "file_upload"

    def __init__(self, server_address, bind_and_activate=True):
        self.server_address = server_address
        self.socket = socket(self.address_family, self.socket_type)
        self.user_account = None
        if bind_and_activate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise
        self.run()

    def operation_menu(self, head_dic):
        if head_dic["cmd_type"] == "login":
            self.login(head_dic)
        elif head_dic["cmd_type"] == "print_quota":
            self.print_quota()
        elif head_dic["cmd_type"] == "print_directory":
            self.print_directory()
        elif head_dic["cmd_type"] == "print_download_list":
            self.print_download_list()
        elif head_dic["cmd_type"] == "create_directory":
            self.create_directory(head_dic)
        elif head_dic["cmd_type"] == "remove_directory":
            self.remove_directory(head_dic)
        elif head_dic["cmd_type"] == "turn_to_directory":
            self.turn_to_directory(head_dic)
        elif head_dic["cmd_type"] == "download_file":
            self.download_file(head_dic)
        elif head_dic["cmd_type"] == "upload_file":
            self.upload_file(head_dic)
        else:
            return

    def download_file(self, head_dic):
        download_file_path = os.path.join(user_file, head_dic["filename"])
        print(download_file_path)
        print(head_dic)
        if not os.path.isfile(download_file_path):
            print("not in 1")
            download_file_path = os.path.join(settings.DLD_FILE, head_dic["filename"])
            print("2,", download_file_path)
            if not os.path.isfile(download_file_path):
                self.send_msg(cmd_type="download_file",
                              res=0,
                              msg="this file doesn't exist")
                return
        md5_download = myfunctools.create_file_md5(download_file_path)
        file_size_download = os.path.getsize(download_file_path)
        seek_num = 0
        if head_dic["file_size"]:
            seek_num = head_dic["file_size"]
            if file_size_download == head_dic["file_size"]:
                self.send_msg(cmd_type="download_file", res=2,
                              msg="you have already downloaded this file completely",
                              file_size=file_size_download)
                return
            else:
                self.send_msg(cmd_type="download_file", res=1,
                              msg="you have download this file partial ,now continue downloading.",
                              file_size=file_size_download)
        else:
            self.send_msg(cmd_type="download_file", res=1, md5=md5_download, file_size=file_size_download)

        send_size = 0
        with open(download_file_path, "rb") as f:
            f.seek(seek_num)
            while send_size < (file_size_download - seek_num):
                cont = f.read(8192)
                self.conn.send(cont)
                send_size += len(cont)
            else:
                print("\ncompleting download 100.00%")

    def upload_file(self, head_dic):
        if not myfunctools.check_quota_enough(user_account, head_dic["file_size"]):
            self.send_msg(cmd_type="upload_file", res=0, msg="your quota is not enough to upload this file.")
            return

        seek_num = 0
        upload_file_path = os.path.join(user_file, os.path.basename(head_dic["filename"]))

        if os.path.isfile(upload_file_path):
            file_size_exist = os.path.getsize(upload_file_path)
            if file_size_exist < head_dic["file_size"]:
                message = "this file has uploaded partial,now continue to upload the rest part."
                self.send_msg(cmd_type="upload", res=1, msg=message, file_size=file_size_exist)
                print(file_size_exist)
                seek_num = file_size_exist
            elif file_size_exist == head_dic["file_size"]:
                message = "this file has already existed."
                self.send_msg(cmd_type="upload", res=0, msg=message, file_size=file_size_exist)
                print(file_size_exist)
                return
        else:
            self.send_msg(cmd_type="upload", res=1, msg="begin to upload", file_size=0)

        with open(upload_file_path, "wb") as f:
            f.seek(seek_num)
            recv_size = 0
            while recv_size < head_dic["file_size"]:
                recv_data = self.conn.recv(8192)
                f.write(recv_data)
                recv_size += len(recv_data)
                sys.stdout.write("#")
                sys.stdout.flush()
        md5_download = myfunctools.create_file_md5(upload_file_path)
        print(upload_file_path)
        print(md5_download)
        if md5_download == head_dic["md5"]:
            self.send_msg(cmd_type="upload_file", msg="received file is your sent file,upload file successfully")
        else:
            self.send_msg(cmd_type="upload_file", msg="we received wrong file")

    def remove_directory(self, head_dic):
        global user_file
        print(user_file)
        msg = myfunctools.remove_dir(user_file, head_dic["msg"])
        self.send_msg(cmd_type="remove_directory", msg=msg)

    def turn_to_directory(self, head_dic):
        global user_file
        global user_account
        res, msg, file_path = myfunctools.turn_to_dir(user_file, head_dic["msg"], user_account)
        if res:
            user_file = file_path
            self.send_msg(cmd_type="turn_to_directory", msg=msg)
        else:
            self.send_msg(cmd_type="turn_to_directory", msg=msg)

    def create_directory(self, head_dic):
        res = myfunctools.create_dir(user_file, head_dic["msg"])
        self.send_msg(cmd_type="create_directory", msg=res)

    def print_msg(self, cmd, file):
        myfunctools.print_directory(file)
        size = os.path.getsize(settings.PRINT_FILE)
        self.send_msg(cmd_type=cmd, file_size=size)
        print("print_msg(self, cmd, file)", size)
        self.send_file(settings.PRINT_FILE)

    def print_download_list(self):
        # self.print_msg(cmd="print_download_list", file=settings.DLD_FILE)
        myfunctools.print_directory(settings.DLD_FILE)
        size = os.path.getsize(settings.PRINT_FILE)
        self.send_msg(cmd_type="print_download_list", file_size=size)
        self.send_file(settings.PRINT_FILE)

    def print_quota(self):
        res = myfunctools.print_quota(user_account)
        self.send_msg(cmd_type="print_quota", msg=res)

    def run(self):
        while True:  # 程序开始不断的循环
            self.conn, self.client_addr = self.get_request()
            print("from client: ", self.client_addr)
            while True:
                # try:
                head_struct = self.conn.recv(4)
                # print(head_struct)
                if not head_struct:
                    continue
                head_len = struct.unpack("i", head_struct)[0]
                head_json = self.conn.recv(head_len).decode(self.coding)
                head_dic = json.loads(head_json)

                self.operation_menu(head_dic)

    def login(self, head_dic):
        if head_dic["cmd_type"] == "login":
            login_res = login.login(head_dic["res"][0], head_dic["res"][1])
            global user_account
            global user_file
            user_account = head_dic["res"][1]
            user_file = settings.USER_FILE % user_account
            self.send_msg(cmd_type="login", res=[login_res[0], login_res[1]])

    def send_msg(self, cmd_type=None, res=None, msg=None, md5=None, filename=None, file_size=None):
        dic = {
            "cmd_type": cmd_type,
            "res": res,
            "msg": msg,
            "md5": md5,
            "filename": filename,
            "file_size": file_size
        }
        dic_json = json.dumps(dic)
        dic_bytes = dic_json.encode("utf-8")
        head_dic = struct.pack("i", len(dic_bytes))
        self.conn.send(head_dic)
        self.conn.send(dic_bytes)

    def print_directory(self):
        myfunctools.print_directory(user_file)
        size = os.path.getsize(settings.PRINT_FILE)
        self.send_msg(cmd_type="print_directory", file_size=size)
        self.send_file(settings.PRINT_FILE)

    def send_file(self, file):

        send_size = 0
        with open(file, "rb") as f:
            for line in f:
                self.conn.send(line)
                send_size += len(line)
                # print(send_size)
            else:
                print("send file completely")

    def server_bind(self):  # 绑定ip及端口的程序
        if self.allow_reuse_address:
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 看是否要复用地址
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()  # 查询自身的ip地址与端口

    def server_activate(self):
        self.socket.listen(self.request_queue_size)

    def server_close(self):
        self.socket.close()

    def get_request(self):
        return self.socket.accept()

    def close_request(self, request):
        request.close()



