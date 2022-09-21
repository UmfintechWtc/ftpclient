#!/usr/local/bin/python3
# coding: utf-8
import os
import json

from client import *
from conf.get_parse import *
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, send_from_directory

port = "8888"
host_ip = socket.gethostbyname(socket.gethostname())
current_path = os.getcwd()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = current_path

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username")
    password = request.form.get("password")
    ftphost = request.form.get("ftphost")
    ftpport = request.form.get("ftpport")
    if username != "{}".format(get_conf("username")):
        return render_template("login.html",msg="用户名错误")
    elif password != "{}".format(get_conf("password")):
        return render_template("login.html", msg="密码错误")
    elif ftphost != '{}'.format(get_conf("ftp_host")) or ftpport != '{}'.format(get_conf("ftp_port")):
        return render_template("login.html", msg="ftp连接异常")
    elif username == "{}".format(get_conf("username")) and password == "{}".format(get_conf("password")) and ftphost == '{}'.format(get_conf("ftp_host")) and ftpport == '{}'.format(get_conf("ftp_port")):
        return redirect("/index")

@app.route('/index', methods=['GET', 'POST', 'PUT'])
def index():
    if request.method == "PUT":
        cmd = request.form.get('cmd', type=str, default=None)
        if len(cmd.split(" ")) <= 1:
            return "请指定需要下载的文件; Usage: get [filename]"
        else:
            filename = os.path.dirname(cmd.split(" ")[1])
            filepath = os.path.relpath(cmd.split(" ")[1])
        try:
            return send_from_directory(filepath, filename, as_attachment=True)
        except Exception as e:
            return "{} download failed".format(filepath)
    elif request.method == "POST":
        cmd = request.form.get('cmd', type=str, default=None)
        response = json.dumps(main(cmd))
        return response,200,{"Content-Type":"application/json"}
    else:
        return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        filename = request.files['filename']
        print (filename)
        try:
            filename.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(filename.filename)))
            return 'upload file [{}] to {} success'.format(filename, current_path), 500, {"Content-Type": "application/json"}
        except Exception as e:
            return 'upload file [{}] to {} failed'.format(filename, current_path), 500, {"Content-Type": "application/json"}
    else:
        return render_template('index.html')

@app.route("/download", methods=['GET'])
def download_file(filename):
    return send_from_directory("/home/wangtianci/test/", "client.py", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
