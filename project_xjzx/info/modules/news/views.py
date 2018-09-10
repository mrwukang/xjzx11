#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import render_template

from info.modules.news import news_blue


@news_blue.route("/")
def index():
    return render_template("admin/index.html")
    # return "hello"
