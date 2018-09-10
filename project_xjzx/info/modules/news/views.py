#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import render_template

from info.modules.news import news_blue


@news_blue.route("/news")
def index():
    return render_template("news/index.html")
