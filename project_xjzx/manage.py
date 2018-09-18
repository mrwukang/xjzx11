#!/usr/bin/python3
# -*- coding:utf-8 -*-
import logging

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app
from info.models import db, User

app = create_app("development")

manager = Manager(app)
# 数据库迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@manager.option("-n", dest="name")
@manager.option("-p", dest="password")
def createadmin(name, password):
    """创建管理员用户"""
    if not all([name, password]):
        print("参数不足")
        return
    try:
        if User.query.filter_by(mobile=name).count() > 0:
            print("该用户名已经存在")
            return
    except Exception as e:
        logging.error(e)
        print("数据库连接失败")
        return
    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        print("数据库连接失败")
        return
    print("管理员创建成功")


if __name__ == '__main__':
    manager.run()
