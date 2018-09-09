#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import Blueprint

news_blue = Blueprint("news", __name__)

from modules.news import views
