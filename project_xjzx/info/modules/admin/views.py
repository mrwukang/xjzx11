# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
from flask import render_template, request, redirect, session, current_app, jsonify

from info import constants
from info.models import User, News, db, Category
from info.modules.admin import admin_blueprint
from info.response_code import RET
from info.utils.image_storage import storage


@admin_blueprint.route("/")
def index():
    user_id = session.get("admin_id")
    user = User.query.get(user_id)
    user_info = user.to_admin_dict()
    return render_template("admin/index.html", data=user_info)


@admin_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """登录功能"""

    # 如果为get方式，则显示登录窗口
    if request.method == "GET":
        if session.get("admin_id") and session.get("is_admin"):
            return redirect("/admin/")
        return render_template("admin/login.html")

    # 如果为post方式请求，则验证提交的数据
    username = request.form.get("username")
    password = request.form.get("password")
    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不足")
    try:
        user = User.query.filter_by(mobile=username, is_admin=True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="数据查询失败")
    if not user:
        return render_template("admin/login.html", errmsg="用户不存在")
    if not user.check_password(password):
        return render_template("admin/login.html", errmsg="密码错误")

    # 如果数据没有问题，则登录
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="数据更新失败")
    session["user_id"] = user.id
    session["admin_id"] = user.id
    session["nick_name"] = user.nick_name
    session["is_admin"] = True
    return redirect("/admin")


@admin_blueprint.route('/logout')
def logout():
    """退出登录功能"""
    session.pop("admin_id", None)
    session.pop("nick_name", None)
    session.pop("is_admin", None)
    session.pop("user_id", None)
    return redirect("/admin/login")


@admin_blueprint.route("/user_count")
def user_count():
    """用户统计"""
    # 用户总数
    count_total = User.query.filter_by(is_admin=False).count()
    # 现在的时间
    now = datetime.now()
    # 本月一号凌晨零点的时间
    month_first = datetime(now.year, now.month, 1)
    count_month = User.query.filter(User.create_time >= month_first).filter_by(is_admin=False).count()
    # 今天凌晨零点的时间
    day_first = datetime(now.year, now.month, now.day)
    count_day = User.query.filter(User.create_time >= day_first).filter_by(is_admin=False).count()

    # 生成最近一个月每天的时间和活跃用户的数量
    active_count = []
    active_date = []
    for i in range(30):
        begin_time = day_first - timedelta(i)
        end_time = day_first - timedelta(i-1)
        active_date.append(begin_time.strftime("%Y-%m-%d"))
        count = 0
        try:
            count = User.query.filter(User.update_time >=begin_time, User.update_time < end_time, User.is_admin==False).count()
        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)

    active_count.reverse()
    active_date.reverse()

    data = {
        "count_total": count_total,
        "count_month": count_month,
        "count_day": count_day,
        "active_count": active_count,
        "active_date": active_date,
    }
    return render_template("admin/user_count.html", data=data)


@admin_blueprint.route("/user_list")
def user_list():
    """用户列表"""
    try:
        current_page = int(request.args.get("page", 1))
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1

    try:
        pagination = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(current_page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        total_page = pagination.pages
        user_lists = pagination.items
        user_info = [user.to_admin_dict() for user in user_lists]
        data = {
            "current_page": current_page,
            "total_page": total_page,
            "user_info": user_info
        }
    except Exception as e:
        current_app.logger.error(e)
        data = {
            "current_page": 1,
            "total_page": 1,
            "user_info": [],
        }
    return render_template("admin/user_list.html", data=data)


@admin_blueprint.route("/news_review", methods=["GET", "POST"])
def news_review():
    """新闻审核"""
    try:
        current_page = int(request.args.get("page", 1))
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
    # keywords = request.args.get("keywords", "")
    keywords = request.form.get("keywords", "")

    try:
        filters = []
        if keywords:
            filters.append(News.title.contains(keywords))
        pagination = News.query.order_by(News.create_time.desc()).filter(*filters).paginate(current_page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        total_page = pagination.pages
        news_list = pagination.items
        news_info = [news.to_review_dict() for news in news_list]
        data = {
            "current_page": current_page,
            "total_page": total_page,
            "news_info": news_info,
        }
    except Exception as e:
        current_app.logger.error(e)
        data = {
            "current_page": 1,
            "total_page": 1,
            "news_info": [],
        }
    return render_template("admin/news_review.html", data=data)


@admin_blueprint.route("/news_review_detail", methods=["GET", "POST"])
def news_review_detail():
    """新闻审核的详情页"""

    # 如果是以get方式提交，则显示新闻的信息
    if request.method == "GET":
        news_id = int(request.args.get("news_id"))
        if not news_id:
            return render_template("admin/news_review_detail.html", errmsg="未接收到新闻ID")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_review_detail.html", errmsg="数据库查询失败")
        if not news:
            return render_template("admin/news_review_detail.html", errmsg="未查询到新闻")
        data = {
            "news_info": news.to_edit_dict(),
        }
        return render_template("admin/news_review_detail.html", data=data)

    # 如果是以post请求提交，则接受参数
    # 并将接受到的参数存储到数据库中
    try:
        news_id = int(request.json.get("news_id"))
        action = request.json.get("action")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="获取数据失败")
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    if action not in ["accept", "reject"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 根据获得的news_id，从数据库查询到对应的news
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到此新闻")

    # 如果action为accept，则改变此新闻的status为0
    if action == "accept":
        news.status = 0

    # 如果action为reject，则修改此新闻的status为-1，并记录拒绝原因
    elif action == "reject":
        try:
            reason = request.json.get("reason")
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="获取拒绝原因失败")
        if not reason:
            return jsonify(errno=RET.NODATA, errmsg="未填写拒绝原因")
        news.reason = reason
        news.status = -1

    # 将修改后的news提交到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据存储失败")
    return jsonify(errno=RET.OK, errmsg="操作成功")


@admin_blueprint.route("/news_edit")
def news_edit():
    """新闻版式编辑"""
    try:

        current_page = int(request.args.get("page", 1))
    except Exception as e:
        current_app.logger.error(e)
        current_page = 1
    keywords = request.args.get("keywords", "")
    try:
        pagination = News.query
        if keywords:
            pagination = pagination.filter(News.title.contains(keywords))
        pagination = pagination.order_by(News.create_time.desc()).paginate(current_page,
                                                                           constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        total_page = pagination.pages
        news_list = pagination.items
        news_info = [news.to_review_dict() for news in news_list]
        data = {
            "current_page": current_page,
            "total_page": total_page,
            "news_info": news_info,
        }
    except Exception as e:
        current_app.logger.error(e)
        data = {
            "current_page": 1,
            "total_page": 1,
            "news_info": [],
        }
    return render_template("admin/news_edit.html", data=data)


@admin_blueprint.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():
    """新闻版式编辑"""

    if request.method == "GET":
        # 如果请求方式为get，则根据接受到的news_id选择要展示的新闻详情
        news_id = int(request.args.get("news_id"))
        if not news_id:
            return render_template("admin/news_edit_detail.html", errmsg="未接收到新闻ID")

        try:
            news = News.query.get(news_id)
            categorys = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", errmsg="数据库查询失败")
        if not all([news, categorys]):
            return render_template("admin/news_edit_detail.html", errmsg="未查询到新闻或者新闻分类信息")

        # 如果数据可以查询到，则返回的数据包含新闻信息和所有的新闻分类信息
        data = {
            "news_info": news.to_edit_dict(),
            "category_list": [category.to_dict() for category in categorys]
        }
        return render_template("admin/news_edit_detail.html", data=data)

    # 如果为post请求方式，则将传来的数据保存到数据库中
    news_id = int(request.form.get("news_id"))
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")
    # 对数据进行验证
    if not all([news_id, title, category_id, digest, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 从数据库中查询到当前news_id对应的news对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库连接错误")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到相关新闻信息")

    # 如果上传了图片，则讲图片上传到七牛云服务器，并将云服务器的图片地址保存到数据库中
    if index_image:
        try:
            files = index_image.read()
            print(files)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg="获取图片信息失败")
        try:
            image_url = storage(files)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="图片上传到云服务器失败")
        news.index_image_url = image_url

    # 将新闻的相关信息替换掉，并存储到数据库中
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.content = content
    news.update_time = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库存储失败")

    return jsonify(errno=RET.OK, errmsg="新闻信息修改成功")


@admin_blueprint.route("/news_type")
def news_type():
    """新闻分类管理"""
    try:
        categorys = Category.query.all()
        category_list = [category.to_dict() for category in categorys]
        data = {
            "category_list": category_list,
        }
    except Exception as e:
        current_app.logger.error(e)
        data = {
            "category_list":[]
        }
    return render_template("admin/news_type.html", data=data)


@admin_blueprint.route('/add_category', methods=["POST"])
def add_category():
    """修改或者添加分类"""

    category_id = request.json.get("id")
    category_name = request.json.get("name")
    if not category_name:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断是否有分类id,如果有，则为修改分类信息
    if category_id:
        try:
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

        if not category:
            return jsonify(errno=RET.NODATA, errmsg="未查询到分类信息")

        category.name = category_name
    else:

        # 如果没有分类id，则是添加分类
        category = Category()
        category.name = category_name
        db.session.add(category)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="保存数据成功")

