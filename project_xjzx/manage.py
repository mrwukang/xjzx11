#!/usr/bin/python3
# -*- coding:utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_wtf.csrf import generate_csrf
from info import create_app
from info.models import db

app = create_app("development")

<<<<<<< HEAD


=======
>>>>>>> 6a5b811e04d63d73d11ef9131f2c8533acfaa27d
manager = Manager(app)
# 数据库迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
