#!/usr/local/bin/python3
# coding: utf-8
from flask import Flask
from flask import render_template, request, redirect
import os
# from client import *
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username")
    password = request.form.get("password")
    ftphost = request.form.get("ftphost")
    ftpport = request.form.get("ftpport")
    if username != "wtc":
        return render_template("login.html",msg="用户名错误")
    elif password != "wtc.com":
        return render_template("login.html", msg="密码错误")
    elif ftphost != '1.1.1.1' or ftpport != '21':
        return render_template("login.html", msg="ftp连接异常")
    elif username == "wtc" and password == "wtc.com" and ftphost == "1.1.1.1" and ftpport == "21":
        return redirect("/index")

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        print (request.data,"name is wtc")
        cmd = request.form.get('cmd', type=str, default=None)
        exec_result=os.popen(cmd).read()
        return render_template('index.html', result=exec_result, cmd=cmd)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)