#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import Blueprint

user_blueprint = Blueprint("user", __name__, url_prefix="/user")

from info.modules.users import views

