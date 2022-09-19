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
    if username == "wtc" and password == "wtc.com":
        return redirect("/index")
    else:
        return render_template("login.html",msg="error")

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