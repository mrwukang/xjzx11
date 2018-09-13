# -*- coding:utf-8 -*-
from flask import render_template, current_app,jsonify, abort, g

from info.modules.news import news_blueprint
from info.models import News
from info.response_code import RET
from info import constants
from info import db

# from info.utils.common import user_login
from info.utils.common import user_login


@news_blueprint.route("/<int:news_id>")
@user_login
def news_detail(news_id):
    # user_id = session.get("user_id")
    # try:
    #     user = User.query.get(user_id) if user_id else None
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    # 在新闻表中查找点击量在前六位的新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    click_news_list = [news.to_click_dict() for news in news_list]

    news = News.query.get(news_id)
    if not news:
        abort(404)
    news.clicks += 1
    db.session.commit()



    data = {
        "news": news.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
    }
    return render_template("news/detail.html", data=data)
