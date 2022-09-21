#!/usr/local/bin/python3
# coding: utf-8
import os
import json

from client import *
from conf.get_parse import *
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, send_from_directory

print (get_conf("username"))