# -*- coding: utf-8 -*-

from flask import render_template, current_app, session, request, jsonify,g

from info.models import News, User, Category
from info.modules.index import index_blueprint
from info import constants
from info.response_code import RET
from info.utils.common import user_login


@index_blueprint.route("/")
@user_login
def index():

    """返回首页"""

    try:
        # 在新闻表中查找点击量在前六位的新闻
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    click_news_list = [news.to_click_dict() for news in news_list]

    try:
        # 在新闻分类表中查询所有分类的name
        categorys_list = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    categorys_list2 = [category.to_dict() for category in categorys_list]

    data = {
        "user_info": g.user.to_index_dict() if g.user else None,
        "click_news_list": click_news_list,
        "categorys_list": categorys_list2,
            }
    return render_template("news/index.html", data=data)


@index_blueprint.route('/newslist')
def newslist():
    """新闻列表展示的功能"""
    args_dict = request.args
    try:
        cur_page = int(args_dict.get("page"))  # 当前页数
        category_id = args_dict.get("cid")  # 分类ID
        per_page = int(args_dict.get("per_page"))  # 每页多少数据
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if not all([cur_page, category_id, per_page]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 如果是“最新”分组，则查询所有新闻
    # 即如果分类id不为0， 则添加对于分类id的过滤
    pagination = News.query
    if category_id != "0":
        pagination = pagination.filter(News.category_id == category_id)
    try:
        pagination = pagination.order_by(News.id.desc()).paginate(cur_page, per_page, False)
        news_list = pagination.items
        total_page = pagination.pages
        news_dict_list = [news.to_basic_dict() for news in news_list]
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    data = {
        "errno": RET.OK,
        "errmsg": "数据传递成功",
        "cid": category_id,
        "cur_page": cur_page,
        "totalPage": total_page,
        "current_page": cur_page,
        "newsList": news_dict_list
    }
    return jsonify(data)




# @index_blueprint.route('/favicon.ico')
# def favicon():
#     return current_app.send_static_file("news/images")
