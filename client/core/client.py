# _*_coding:utf-8_*_

import hashlib
import json
import os
import socket
import struct
import sys


class Client:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    allow_reuse_address = True
    max_packet_size = 8192
    coding = "utf-8"
    request_queue_size = 5

    def __init__(self, server_address):
        self.server_address = server_address
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.client_connect()
        self.run()

    def run(self):
        """每个登录成功的管理员运行此函数"""
        self.login()
        print(self.cmd_msg)
        while True:
            cmd = input(">>: ").strip()
            if cmd in [str(i) for i in range(1, 9)]:
                self.operation_dic[cmd](self)
            else:
                print("please input number between 1 to 8")

    def print_msg_quota(self, cmd):
        self.send_msg(cmd_type=cmd)
        # self.receive_msg()
        cont = self.receive_msg()
        return cont["msg"]

    def print_msg(self, cmd):
        self.send_msg(cmd_type=cmd)
        # self.receive_msg()
        cont = self.receive_file(self.receive_msg())
        return cont.decode("GBK")

    def print_directory(self):
        res = self.print_msg("print_directory")
        print(res)

    def print_quota(self):
        res = self.print_msg_quota("print_quota")
        print(res)

    def receive_file(self, head_dic):
        total_size = head_dic["file_size"]
        recv_data = b""
        recv_size = 0
        while recv_size < total_size:
            recv_data_part = self.socket.recv(8196)
            recv_data += recv_data_part
            recv_size += len(recv_data_part)
        return recv_data

    def print_download_list(self):
        res = self.print_msg("print_download_list")
        print(res)

    def create_directory(self):
        file_path_list = self.directory_analysis()
        self.send_msg(cmd_type="create_directory", msg=file_path_list)
        res = self.receive_msg()
        print(res["msg"])

    def turn_to_directory(self):
        print("input 'home' to get back to home directory")
        file_path_list = self.directory_analysis()
        self.send_msg(cmd_type="turn_to_directory", msg=file_path_list)
        res = self.receive_msg()
        print(res["msg"])

    def remove_directory(self):
        file_path_list = self.directory_analysis()
        self.send_msg(cmd_type="remove_directory", msg=file_path_list)
        res = self.receive_msg()
        print(res["msg"])

    def directory_analysis(self):
        while True:
            directory = input("please input directory name,\n"
                              "multi-layer directory split with '/'.\n"
                              "each directory name can only include numbers or letters\n").strip()

            directs = directory.split("/")
            if not any(directs):
                print("your input is illegal,please input again")
                continue
            for index in range(len(directs)):
                directs[index] = directs[index].strip()
            return directs

    def download_file(self):
        while True:
            file_name = input("please enter filename: ").strip()
            if not any(file_name):
                print("empty filename")
                continue
            if file_name == "q":
                return
            break
        download_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")
        file_path = os.path.join(download_path, file_name)
        seek_num = 0
        if os.path.isfile(file_path):
            file_size_exist = os.path.getsize(file_path)
            seek_num = file_size_exist
            self.send_msg(cmd_type="download_file", filename=file_name, file_size=file_size_exist)
            head_dic = self.receive_msg()
            total_size = head_dic["file_size"] - file_size_exist
        else:
            self.send_msg(cmd_type="download_file", filename=file_name)
            head_dic = self.receive_msg()
            total_size = head_dic["file_size"]

        if head_dic["res"] != 1:
            print(head_dic["msg"])
            return

        with open(file_path, "wb") as f:
            f.seek(seek_num)
            recv_size = 0
            print("completing progressbar : ", end="")
            while recv_size < total_size:
                recv_data = self.socket.recv(8192)
                f.write(recv_data)
                recv_size += len(recv_data)
                sys.stdout.write("#")
                sys.stdout.flush()
        md5 = self.create_file_md5(file_path)
        if md5 == head_dic["md5"]:
            print("\nreceived file is the same with download file, download file successfully")
        else:
            print("\nwe download wrong file")

    def upload_file(self):

        while True:
            file_name = input(
                "which file do you want to upload?\nplease enter complete complete directory and filename\n")
            if file_name == "q":
                return
            if not os.path.isfile(file_name):
                print("the filename you input doesn't exist")
                continue
            break
        md = self.create_md5(file_name)
        file_size = os.path.getsize(file_name)
        # print("fie_size", file_size)
        self.send_msg(cmd_type="upload_file", md5=md, filename=file_name, file_size=file_size)
        # f = file_bytes = open(file_name,"rb")
        head_dic = self.receive_msg()
        # print(head_dic)
        if head_dic["res"] == 0:
            print(head_dic["msg"])
            return
        else:
            print(head_dic["msg"])
        seek_num = head_dic["file_size"]
        # head_dic_2 = self.receive_msg()

        # print(123)
        send_size = 0
        with open(file_name, "rb") as f:
            f.seek(seek_num)
            print("completing progressbar : ", end="")
            while send_size < (file_size - head_dic["file_size"]):
                cont = f.read(8192)
                self.socket.send(cont)
                send_size += len(cont)
                sys.stdout.write("#")
                sys.stdout.flush()
            else:
                print("\ncompleting upload 100.00%")
                res = self.receive_msg()
                print(res["msg"])

    def create_md5(self, file_path):
        md = hashlib.md5()
        with open(file_path, "rb") as f:
            md.update(f.read())
        return md.hexdigest()

    def compare_file(self, file1, file2):
        md1 = self.create_md5(file1)
        md2 = self.create_md5(file2)
        if md1 == md2:
            return True
        else:
            return False

    def send_msg(self, cmd_type=None, res=None, msg=None, md5=None, filename=None, file_size=None):
        dic = {
            "cmd_type": cmd_type,
            "res": res,
            "msg": msg,
            "filename": filename,
            "md5": md5,
            "file_size": file_size
        }
        dic_json = json.dumps(dic)
        dic_bytes = dic_json.encode("utf-8")
        head_dic = struct.pack("i", len(dic_bytes))
        self.socket.send(head_dic)
        self.socket.send(dic_bytes)

    def receive_msg(self):
        header = self.socket.recv(4)
        header_size = struct.unpack("i", header)[0]
        # print(header_size)
        header_bytes = self.socket.recv(header_size)
        header_json = header_bytes.decode("utf-8")
        header_dic = json.loads(header_json)
        return header_dic

    def client_connect(self):
        self.socket.connect(self.server_address)

    def client_close(self):
        self.socket.close()

    def login(self):
        print("Welcome to File Transport System!".center(60, "*"))
        while True:
            user_account = input("account: ").strip()
            user_password = input("password: ").strip()
            if any(user_account) and any(user_password):
                break
            else:
                print("Wrong account or password,please try again.")
                continue

        self.send_msg(cmd_type="login", res=[user_account, user_password])
        res = self.receive_msg()
        if res["res"][0]:
            print(res["res"][1])
        else:
            print(res["res"][1])
            self.login()

    def cmd_check(self):
        while True:
            num = input("please input your command").strip()
            if num not in [str(i) for i in range(1, 9)]:
                print("wrong command number")
                continue
            else:
                return self.operation_dic[num]()

    def create_file_md5(self, file_path):
        md = hashlib.md5()
        with open(file_path, "rb") as f:
            while True:
                f_part = f.read(8196)
                if not f_part:
                    break
                md.update(f_part)
        return md.hexdigest()

    cmd_msg = """
    *******File Transport System*******
           1.print my directory(打印我的云空间)
           2.print my quota(查看空间使用情况)
           3.upload file(上传文件)
           4.download file(下载文件)
           5.create directory(新建目录)
           6.turn to directory(转到其他目录)
           7.remove file or directory(every file will be deleted)(删除文件或者文件夹下所有文件)
           8.exit(退出客户端)
           please input number between 1 to 8,
           you can eixt sub menu by input "q"
               """
    # 操作系统的菜单, 跳转到指定函数
    operation_dic = {
        "1": print_directory,
        "2": print_quota,
        "3": upload_file,
        "4": download_file,
        "5": create_directory,
        "6": turn_to_directory,
        "7": remove_directory,
        "8": exit
    }
