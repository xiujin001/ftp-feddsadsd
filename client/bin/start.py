# _*_ coding=utf-8 _*_
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from core import main

# BASE_DIR = settings.BASE_DIR
# from conf import settings

if __name__ == '__main__':
    main.main()
