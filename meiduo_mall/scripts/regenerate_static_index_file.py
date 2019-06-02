#!/usr/bin/env python

"""
功能:手动生成首页静态html文件
使用方法:
    ./regenerate_static_index_file.py
"""
import sys


# 添加导包路径
sys.path.insert(0, '../')
sys.path.insert(0, '../meiduo_mall/apps')

# 使用django的设置,配置使用哪个配置文件
# import os
# if not os.getenv('DJANGO_SETTINGS_MODULE'):
#     os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# django初始化相关
import django
django.setup()


from contents.crons import generate_static_index_file


if __name__ == "__main__":
    generate_static_index_file()