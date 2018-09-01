# _*_ coding=utf-8 _*_
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from core import server



def main():
    server_obj = server.Server(("127.0.0.1", 6666))
