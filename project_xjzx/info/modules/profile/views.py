#!/usr/bin/python3
# -*- coding:utf-8 -*-
from  datetime import datetime
from flask import session, make_response, request, jsonify, g, render_template, current_app, redirect

from info.models import News, User, Category
from info.modules.profile import user_blueprint
from info.utils.common import user_login
from info.response_code import RET
from info import db
from info import constants
from info.utils.image_storage import storage


@user_blueprint.route('/info')
@user_login
def get_user_info():
    """打开个人中心"""
    data = {
        "user_info": g.user.to_dict()
    }
    return render_template("news/user.html", data=data)


@user_blueprint.route('/user_base_info', methods=["POST", "GET"])
@user_login
def user_base_info():
    """
        更新用户基本信息
        1. 获取用户登录信息
        2. 获取到传入参数
        3. 更新并保存数据
        4. 返回结果
        :return:
        """
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user_info": user.to_dict()})

    # 2. 获取到传入参数
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if gender not in (['MAN', 'WOMAN']):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3. 更新并保存数据
    user.update_time = datetime.now()
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将 session 中保存的数据进行实时更新
    session["nick_name"] = nick_name




    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")


@user_blueprint.route('/pic_info', methods=['GET', 'POST'])
@user_login
def pic_info():
    """
            用户头像
            1. 获取用户登录信息
            2. 获取到上传头像
            3. 更新并保存数据
            4. 返回结果
            :return:
            """
    user = g.user
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user_info": user.to_dict()})
    try:
        files = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取文件出错")
    try:
        url_path = storage(files)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="头像上传到云服务器失败")
    print(url_path)

    user.avatar_url = url_path
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="连接服务器失败")
    data = {
        "avatar_url": constants.QINIU_DOMIN_PREFIX + user.avatar_url
    }
    return jsonify(errno=RET.OK, errmsg="头像上传成功", data=data)


@user_blueprint.route('/pass_info', methods=['GET', 'POST'])
@user_login
def pass_info():
    """修改密码页面"""
    user = g.user
    if request.method == "GET":
        return render_template('news/user_pass_info.html', data={"user_info": user.to_dict()})

    # 如果为post请求，即修改密码请求发送时
    password_dict = request.json
    old_password = password_dict.get("old_password")
    new_password = password_dict.get("new_password")
    new_password2 = password_dict.get("new_password2")

    # 验证传入的参数是否正确
    if not all([old_password, new_password, new_password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    if new_password != new_password2:
        return jsonify(errno=RET.DATAERR, errmsg="两次密码不一致")
    user = g.user
    if not user.check_password(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="原密码输入错误")

    # 将密码替换为新密码
    user.password = new_password
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="密码修改成功")


@user_blueprint.route('/user_follow', methods=['GET'])
@user_login
def user_follow():
    """展示当前用户的关注列表"""

    user = g.user
    try:
        page = int(request.args.get("page"))
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    try:
        pagination = user.authors.order_by(User.id.desc()).paginate(page,constants.USER_FOLLOWED_MAX_COUNT, False)
        current_page = page
        total_pages = pagination.pages
        author_list = [author.to_dict() for author in pagination.items]
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
        total_pages = 1
        author_list = []
    data = {
        "current_page": current_page,
        "total_pages": total_pages,
        "author_list": author_list,
    }

    return render_template('news/user_follow.html', data=data)


@user_blueprint.route('/collection', methods=['GET'])
@user_login
def collection():
    """显示当前用户收藏的新闻"""
    try:
        page = int(request.args.get("page", 1))
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    try:
        pagination = user.collection_news.order_by(News.id.desc()).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = page
        total_pages = pagination.pages
        news_list = [news.to_dict() for news in pagination.items]
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
        total_pages = 1
        news_list = []
    data = {
        "current_page": current_page,
        "total_page": total_pages,
        "news_list": news_list,

    }
    return render_template('news/user_collection.html', data=data)


@user_blueprint.route('/user_news_release', methods=["GET", "POST"])
@user_login
def user_news_release():
    """发布新闻"""
    user = g.user
    if request.method == "GET":
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            categories = []
        categories_list = [category.to_dict() for category in categories]

        # 显示发布新闻的页面
        return render_template('news/user_news_release.html', data={"categories": categories_list})

    # 如果是用post方式提交数据
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    source = "个人发布"
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    # 判断是否有值
    if not all([title, category_id, digest, content, source]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 读取图片信息
    path_url = ""
    if index_image:
        try:
            image_files = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg="图片读取错误")

        # 将图片上传到七牛云
        try:
            path_url = storage(image_files)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 将新闻信息存储至数据库
    news = News()
    news.title = title
    news.source = source
    news.digest = digest
    news.content = content
    if path_url:
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + path_url
    news.category_id = category_id
    news.user_id = user.id
    news.status = 1
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库存储失败")

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="发布成功，等待审核")


@user_blueprint.route('/user_news_list')
@user_login
def user_news_list():
    """显示当前用户已经发布的新闻"""
    try:
        page = int(request.args.get("page", 1))
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    user = g.user
    try:
        pagination = user.news_list.order_by(News.id.desc()).paginate(page, constants.USER_NEWS_LIST_MAX_COUNT, False)
        current_page = page
        total_pages = pagination.pages
        news_lists = [news.to_review_dict() for news in pagination.items]
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
        total_pages = 1
        news_lists = []
    data = {
        "current_page": current_page,
        "total_page": total_pages,
        "news_list": news_lists,

    }
    return render_template('news/user_news_list.html', data=data)




