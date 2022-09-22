#!/usr/bin/python3
# -*- coding: utf-8 -*-
# author:wtc
"""
    Created on 2022/7/25 21:22
"""
import os
import sys
import json
import tqdm
import struct
import socket

class ConnftpClient:
    def __init__(self, host, port, buffer_size=102400, timeout=10):
        """
        :param host: FTP登录地址
        :param port: FTP登录端口
        :param buffer_size: 缓冲区大小
        :param timeout: FTP连接超时时间
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.buffer = buffer_size
        self.client = socket.socket()
        self.client.settimeout(self.timeout)

    def _connftp(self):
        """
        :return: 返回FTP连接结果
        """
        try:
            self.client.connect((self.host, int(self.port)))
            res = self.client.recv(self.buffer).decode()
            if res.startswith("220"):
                return "连接FTP地址 {}:{} 成功".format(self.host, self.port)
            else:
                return res
        except Exception as e:
            return "连接FTP地址 {}:{} 异常, 请检查FTP服务端网络地址是否正常".format(self.host, self.port)

    def _login_user(self):
        """
        :return: 返回用户名访问结果
        """
        username = "wtc"
        login_username = "USER " + username + "\n"
        self.client.sendall(login_username.encode())
        rsp = self.client.recv(self.buffer).decode()
        if rsp.startswith("331"):
            return "{}用户访问FTP地址 {}:{} 成功".format(username, self.host, self.port)
        else:
            return "访问FTP地址 {}:{}失败，请检查FTP登录用户名{}是否正常".format(self.host, self.port, username)

    def _login_pass(self):
        """
        :return: 访问FTP密码认证结果
        """
        password = "wtc.com"
        login_password = "PASS " + password + "\n"
        try:
            self.client.sendall(login_password.encode())
            rsp = self.client.recv(self.buffer).decode()
            if rsp.startswith("5"):
                return "认证FTP地址 {}:{}失败，请检查FTP登录用户密码是否正常".format(self.host, self.port)
            else:
                return "认证FTP地址 {}:{} 成功".format(self.host, self.port, password)
        except Exception as e:
            return "访问FTP地址 {}:{} 异常, 请检查用户密码是否正常".format(self.host, self.port)

    def _login_mode(self, mode="PASV"):
        """
        :param mode: 默认为被动模式
        :return: 返回Data Port响应体
        """
        mode = mode + "\n"
        self.client.sendall(mode.encode())
        try:
            for i in range(3):
                rsp = self.client.recv(self.buffer).decode()
                print(rsp.strip("\n"))
                if rsp.startswith("227"):
                    return rsp.split(",")
                else:
                    continue
        except Exception as e:
            pass

    def _login_ftp(self):
        """
        :return: 连接 -> 访问 -> 认证，返回最终结果
        """
        self._login_user()
        self._login_pass()

    def help(self):
        """
        :return: FTP支持CMD指令
        """
        help_msg = """
        · ls - Displays an abbreviated list of a remote directory's files and subdirectories
        · help - Displays descriptions for ftp commands
        · put - Copies a single local file to the remote computer
        · get - Copies a single remote file to the local computer
        · delete - Deletes a single file on a remote computer
        · mkdir - Creates a remote directory
        · rmdir - Deletes a remote directory
        · cd - Changes the working directory on the remote computer
        · quit - Ends the FTP session with the remote computer and exits ftp (same as "bye")
        """
        return help_msg

    def list_files(self, path=None):
        """
        :param path: 查询目录路径
        :return: 当前工作路径下文件目录列表信息
        """
        if path is None or path == "":
            cmd = "LIST" + "\n"
        else:
            cmd = "LIST " + path + "\n"
        self.client.sendall(cmd.encode())

    def get_path(self):
        """
        :return: 当前工作路径
        """
        cmd = "PWD" + "\n"
        self.client.sendall((cmd.encode()))
        try:
            for i in range(2):
                rsp = self.client.recv(self.buffer).decode()
                if rsp.startswith("257"):
                    fmt_rsp = rsp.strip("\n")
                    return fmt_rsp
        except Exception as e:
            pass

    def cwd(self, path=None):
        """
        :param path: 需要进行切换的目录
        :return: 切换后的工作路径
        """
        if path is None or path == "":
            return "需要指明切换路径"
        else:
            path = path
            cmd = "CWD " + path + "\n"
            self.client.sendall(cmd.encode())
            try:
                for i in range(2):
                    rsp = self.client.recv(self.buffer).decode()
                    if rsp.startswith("250"):
                        fmt_rsp = rsp.strip("\n")
                        return fmt_rsp
            except Exception as e:
                pass

    def mkdir(self, path=None):
        """
        :param path: 创建目录路径，不可递归
        :return: 在当前工作路径下创建目录
        """
        if path is None or path == "":
            return "需要指明创建目录；Usage: mkdir [path]"
        else:
            path = path
            cmd = "MKD " + path + "\n"
            self.client.sendall(cmd.encode())
            try:
                for i in range(2):
                    res = self.client.recv(self.buffer).decode()
                    if res.startswith("257"):
                        return res.strip("\r\n")
                    elif res.startswith("550"):
                        return res.strip("\r\n")+", please check {} is exists".format(path)
            except Exception as e:
                pass

    def rmdir(self, path=None):
        """
        :param path: 删除目录路径，不可递归
        :return: 在当前工作路径下删除目录
        """
        if path is None or path == "":
            return "需要指明删除目录；Usage: mkdir [path]"
        else:
            path = path
            cmd = "RMD " + path + "\n"
            self.client.sendall(cmd.encode())
            try:
                for i in range(2):
                    res = self.client.recv(self.buffer).decode()
                    if res.startswith("250"):
                        return path + " " + res.strip("\r\n")
                    elif res.startswith("550"):
                        return res.strip("\r\n") + ", please check {} is exists".format(path)
            except Exception as e:
                pass

    def delete(self, filename=None):
        """
        :param filename: 删除当前路径的某个文件
        :return: 删除当前路径的某个文件
        """
        if filename is None or filename == "":
            return "需要指明删除文件名; Usage: delete [filename] "
        else:
            filename = filename
        cmd = "DELE " + filename + "\n"
        self.client.sendall(cmd.encode())
        try:
            for i in range(2):
                res = self.client.recv(self.buffer).decode()
                if res.startswith("250"):
                    return res.strip("\r\n")
                elif res.startswith("550"):
                    return res.strip("\r\n") + ", please check {} is exists".format(filename)
        except Exception as e:
            pass

    def get_size(self, filename=None):
        """
        :param filename: 指明需要操作的文件
        :return: 获取ftp服务操作文件大小
        """
        cmd = "SIZE " + filename + "\n"
        self.client.sendall(cmd.encode())
        try:
            for i in range(3):
                res = self.client.recv(self.buffer).decode()
                if res.startswith("213"):
                    remote_size = res.strip("\r\n").split(" ")[1]
                    return remote_size
                else:
                    pass
        except Exception as e:
            print(str(e))

    def get_file(self, filename=None):
        """
        :param filename: 指明需要下载的文件
        :return: 下载文件数据流
        """
        if filename is None or filename == "":
            return "请指明需要下载的文件; Usage: get [filename]"
        else:
            filename = filename
        cmd = "RETR " + filename + "\n"
        self.client.sendall(cmd.encode())

    def put_file(self, filename=None):
        """
        :param filename: 指明需要上传的文件
        :return:  上传文件数据流
        """
        if filename is None or filename == "":
            return "请指明需要上传的文件; Usage: put [filename]"
        else:
            filename = filename
        cmd = "STOR " + filename + "\n"
        self.client.sendall(cmd.encode())

    def quit(self):
        """
        :return: 关闭会话并退出ftp连接
        """
        cmd = "QUIT" + "\n"
        self.client.sendall(cmd.encode())
        self.client.close()


class DataFtpClient():
    def __init__(self, host, port, buffer_size=1024, timeout=30):
        """
        :param host: 连接地址
        :param port:  连接端口
        :param buffer_size: 接收缓冲区大小，默认1024 Bytes
        :param timeout: 连接超时，默认30 Seconds
        """
        self.host = host
        self.inc_port = port[-2]
        self.num_port = port[-1].replace(').\r\n', '')
        self.timeout = timeout
        self.buffer = buffer_size
        self.client = socket.socket()
        self.client.settimeout(self.timeout)

    def _connftp(self):
        """
        :return: ftp连接对象
        """
        data_trans = int(self.inc_port) * 256 + int(self.num_port)
        self.client.connect((self.host, data_trans))
        self.client.settimeout(self.timeout)

    def _get_ls_data_trans(self):
        """
        :return: 获取查询文件目录列表
        """
        try:
            recv_data = ''
            while True:
                data_rsp = self.client.recv(self.buffer).decode()
                if len(data_rsp) > 0:
                    data_rsp = data_rsp
                else:
                    break
                recv_data += data_rsp
            return recv_data
        except Exception as e:
            pass

    def get_write_data_trans(self, filename=None, filesize=None):
        """
        :param filename: 文件传输写入文件名
        :param filesize: ftp服务端文件size大小
        :return: 下载进度
        """
        try:
            progress = tqdm.tqdm(range(
                int(filesize)), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            recv_data = b''
            while True:
                data_rsp = self.client.recv(self.buffer).decode()
                if len(data_rsp) > 0:
                    data_rsp = data_rsp.encode()
                else:
                    break
                recv_data += data_rsp
                localOpt.write_local_file(filename, recv_data)
                progress.update(len(data_rsp))
        except Exception as e:
            print(str(e))

    def put_write_data_trans(self, filename=None, filesize=None):
        """
        :param filename: 文件传输写入文件名
        :param filesize: 计算机本地文件size大小
        :return: 下载进度
        """
        try:
            progress = tqdm.tqdm(range(
                int(filesize)), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "r", encoding="utf8") as r_f:
                while True:
                    put_data = r_f.read(self.buffer)
                    if len(put_data) > 0:
                        put_data = put_data.encode()
                    else:
                        break
                    self.client.sendall(put_data)
                    progress.update(len(put_data))
        except Exception as e:
            print (str(e))

    def quit(self):
        """
        :return: exit current session connection
        """
        self.client.close()


class localOpt():
    def local_file_exists(filename):
        """
        :param filename: 判断本地文件是否存在
        :return: 存在 True or 不存在 False
        """
        if filename is None:
            print("请指明一个文件")
            return False
        else:
            return True if os.path.exists(filename) else False

    def write_local_file(filename, data):
        """
        :param filename: 指明需要下载的文件
        :param data: ftp服务端数据文件内容
        :return: 回写数据
        """
        with open(filename, "wb") as w_f:
            w_f.write(data)

    def get_local_file_size(filename):
        """
        :param filename: 获取计算机本地文件size大小
        :return: 本地文件大小
        """
        local_file_size = os.path.getsize(filename)
        return local_file_size

    def compare(local_szie, remote_size, filename):
        """
        :param local_szie: 获取计算机本地文件size大小
        :param remote_size: ftp服务端文件size大小
        :param filename: 操作文件名
        :return: 上传 or 下载文件是否正常
        """
        if int(local_szie) == int(remote_size):
            return "{}文件传输正常，大小为{}字节".format(filename, local_szie)
        else:
            return "{}文件传输异常，大小差异为{}字节".format(filename, int(remote_size) - int(local_szie))


def main(cmd):
    ftp_host = "39.105.101.140"
    ftp_port = "21"
    ConnClient = ConnftpClient(ftp_host, ftp_port)
    ConnClient._connftp()
    ConnClient._login_ftp()
    cmd = cmd
    if cmd.startswith("ls"):
        if len(cmd.split(" ")) == 1:
            path = None
        elif len(cmd.split(" ")) == 2:
            path = cmd.split(" ")[1]
        else:
            return "请指定一个目录进行查询; Usage: ls [path]"
        trans_port_rsp = ConnClient._login_mode()
        ConnClient.list_files(path)
        DataClient = DataFtpClient(ftp_host, trans_port_rsp)
        DataClient._connftp()
        try:
            for i in range(3):
                if i == 0:
                    res = DataClient._get_ls_data_trans()
                else:
                    ConnClient.client.recv(1024).decode()
        except Exception as e:
            pass
        finally:
            DataClient.quit()
            return res
    elif cmd.startswith("get"):
        if len(cmd.split(" ")) == 1:
            return "请指定需要下载的文件; Usage: get [filename]"
        elif len(cmd.split(" ")) == 2:
            filename = cmd.split(" ")[1]
        else:
            return "请指定需要下载的文件; Usage: get [filename]"
        remote_size = ConnClient.get_size(filename)
        if remote_size is None or remote_size == "":
            return "请确认文件{}是否存在".format(filename)
        else:
            trans_port_rsp = ConnClient._login_mode()
            ConnClient.get_file(filename)
            DataClient = DataFtpClient(ftp_host, trans_port_rsp)
            DataClient._connftp()
            try:
                for i in range(3):
                    if i == 0:
                        DataClient.get_write_data_trans(filename, remote_size)
                    else:
                        ConnClient.client.recv(1024).decode()
            except Exception as e:
                pass
            finally:
                local_file_size = localOpt.get_local_file_size(filename)
                localOpt.compare(remote_size, local_file_size, filename)
                DataClient.quit()
    elif cmd.startswith("put"):
        if len(cmd.split(" ")) == 1:
            return "请指定需要上传的文件; Usage: put [filename]"
        elif len(cmd.split(" ")) == 2:
            filename = cmd.split(" ")[1]
        else:
            res = "请指定需要上传的文件; Usage: put [filename]"
            return res
        if localOpt.local_file_exists(filename):
            local_size = localOpt.get_local_file_size(filename)
            trans_port_rsp = ConnClient._login_mode()
            ConnClient.put_file(filename)
            DataClient = DataFtpClient(ftp_host, trans_port_rsp)
            DataClient._connftp()
            DataClient.put_write_data_trans(filename, local_size)
            DataClient.quit()
            ConnClient._login_mode()
            remote_size = ConnClient.get_size(filename)
            local_size = localOpt.get_local_file_size(filename)
            localOpt.compare(local_size, remote_size, filename)

    elif cmd == "pwd":
        res = ConnClient.get_path()
        return res
    elif cmd == "help":
        help_msg = ConnClient.help()
        return help_msg
    elif cmd.startswith("cd"):
        if len(cmd.split(" ")) == 2:
            path = cmd.split(" ")[1]
            res = ConnClient.cwd(path)
            return res
        else:
            return "请指定一个目录进行切换"
    elif cmd.startswith("mkdir"):
        if len(cmd.split(" ")) == 2:
            path = cmd.split(" ")[1]
            res = ConnClient.mkdir(path)
            return res
        else:
            return "需要指明创建路径; Usage: mkdir [path]"
    elif cmd.startswith("rmdir"):
        if len(cmd.split(" ")) == 2:
            path = cmd.split(" ")[1]
            res = ConnClient.rmdir(path)
            return res
        else:
            return "需要指明删除目录;  Usage: rmdir [path]"
    elif cmd.startswith("delete"):
        if len(cmd.split(" ")) == 2:
            filename = cmd.split(" ")[1]
            res = ConnClient.delete(filename)
            return res
        else:
            return "需要指明删除文件名; Usage: delete [filename]"
    elif cmd == "quit" or cmd == "bye":
        ConnClient.quit()
        return "221 Goodbye."
    else:
        return "无效命令，请输入help进行查看"