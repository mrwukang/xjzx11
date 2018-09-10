#!/usr/bin/python3
# -*- coding:utf-8 -*-
import random

from flask import session, make_response, request, jsonify

from info.modules.users import user_blueprint
from info.utils.captcha.captcha import captcha
from info.models import db, User


@user_blueprint.route("/image_code")
def image_code():
    name, text, value = captcha.generate_captcha()
    session['image_code'] = text
    print('%s-----' % text)

    response = make_response(value)
    response.mimetype = 'image/png'
    return response


@user_blueprint.route("/smscode")
def smscode():
    dict1 = request.args
    mobile = dict1.get("mobile")
    imagecode = dict1.get("image_code")
    if imagecode != session["image_code"]:
        return jsonify(result=2)
    code = random.randint(1000, 9999)
    session["smscode"] = code
    print("=============%s" % code)
    status = '000000'
    if status == '000000':
        return jsonify(result=1)
    else:
        return jsonify(result=3)


@user_blueprint.route("/register", methods=["POST"])
def register():
    dict1 = request.form
    mobile = dict.get('mobile')
    smscode = int(dict1.get('smscode'))
    password = dict1.get('password')
    if smscode != session['smscode']:
        return jsonify(result=2)
    user = User.query.filter_by(mobile=mobile)
    print(user)
    if user:
        return jsonify(result=3)
    user = User()
    user.nick_name = mobile
    user.avatar_url = ''
    user.mobile = mobile
    user.password_hash = password
    db.session.add(user)
    db.session.commit()
    return jsonify(result=1)

@user_blueprint.route("/login", methods=["POST"])
def login():
    dict1 = request.form
    mobile = dict1.get('mobile')
    password = dict1.get('password')
    user = User.query.filter_by(mobile=mobile).first()
    if user:
        if user.check_password(password):
            session['user_id'] = user.id
            avatar = user.avatar_url
            nick_name = user.nick_name
            # count_hour()
            return jsonify(result=1, avatar=avatar, nick_name=nick_name)
        else:
            return jsonify(result=3)
    else:
        return jsonify(result=2)


@user_blueprint.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id")
    return jsonify(result=1)


