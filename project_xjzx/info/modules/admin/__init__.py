# -*- coding:utf-8 -*-
from flask import Blueprint

admin_blueprint = Blueprint("admins", __name__)

from info.modules.admin import views



