#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import Blueprint

user_blueprint = Blueprint("profile", __name__, url_prefix="/profile")

from info.modules.profile import views

