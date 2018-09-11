#!/usr/bin/python3
# -*- coding:utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app
from info.models import db
from flask_wtf.csrf import generate_csrf

app = create_app("development")


# @app.after_request
# def after_request(response):
#     csrf_token = generate_csrf()
#     response.set_cookie("csrf_token", csrf_token)
#     return response


manager = Manager(app)
# 数据库迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
