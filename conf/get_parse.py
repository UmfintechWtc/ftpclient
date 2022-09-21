#!/usr/local/bin/python3
# coding: utf-8
import os
import configparser

# 防止远程调用读取配置失败
cfg = configparser.ConfigParser()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg.read(os.path.join(BASE_DIR ,'config.ini'))

def get_conf(query_type):
    if query_type == "username":
        return cfg.get("ftp_info", "username")
    elif query_type == "password":
        return cfg.get("ftp_info", "password")
    elif query_type == "ftp_host":
        return cfg.get("ftp_info", "ftp_host")
    elif query_type == "ftp_port":
        return cfg.get("ftp_info", "ftp_port")
    elif query_type == "listen":
        return cfg.get("server", "listen")
    else:
        return "Usage: username|password|ftp_host|ftp_port|lisetn"