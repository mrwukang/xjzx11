# -*- coding:utf-8 -*-
from flask import render_template, current_app,jsonify, abort, g, request

from info.modules.news import news_blueprint
from info.models import News, Comment, CommentLike, User
from info.response_code import RET
from info import constants
from info import db

# from info.utils.common import user_login
from info.utils.common import user_login


@news_blueprint.route("/<int:news_id>")
@user_login
def news_detail(news_id):
    """  通过新闻的news_id返回新闻的详情页"""

    # 在新闻表中查找点击量在前六位的新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    click_news_list = [news.to_click_dict() for news in news_list]

    # 查询要展示的新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻数据失败")
    if not news:
        abort(404)
    news.clicks += 1
    db.session.commit()

    # 查询当前新闻的所有评论
    try:
        comments = Comment.query.filter(Comment.news_id == news_id, Comment.parent_id == None).order_by(Comment.id.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻评论失败")
    comment_like_ids = []

    # 判断评论是否被本用户点赞
    if g.user:
        comment_ids = [comment_temp.id for comment_temp in comments]
        if len(comment_ids) > 0:
            # 取出当前用户在当前新闻的所有点赞的记录
            comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids), CommentLike.user_id == g.user.id)
            # 记录记录中的所有评论的ID
            comment_like_ids = [comment_like_temp.comment_id for comment_like_temp in comment_likes]
    comment_list = []

    if comments:
        for item in comments:
            comment_dict = item.to_dict()
            if g.user and comment_dict["id"] in comment_like_ids:
                comment_dict["is_like"] = True

            comment_list.append(comment_dict)

    # 判断新闻是否已经被收藏
    is_collected = False
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 当前用户是否关注此作者
    is_followed = False
    if g.user:
        if User.query.filter(User.id == news.user_id).first() in g.user.authors:
            is_followed = True

    # 发送给html模板的数据
    data = {
        "news": news.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "is_collected": is_collected,
        "comments": comment_list,
        "is_followed": is_followed,
    }

    # 返回模板
    return render_template("news/detail.html", data=data)


@news_blueprint.route('/news_collect', methods=['POST'])
@user_login
def news_collect():
    """新闻收藏和取消收藏功能"""

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="连接数据库失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 根据传入的action值的不同，来决定user与news的中间表的数据的增加和删除
    if action == "collect":
        user.collection_news.append(news)
        db.session.commit()
    elif action == "cancel_collect":
        user.collection_news.remove(news)
        db.session.commit()

    return jsonify(errno=RET.OK, errmsg="成功")


@news_blueprint.route('/add_comment', methods=['POST'])
@user_login
def add_comment():
    """ 添加评论到数据库"""

    news_id = request.json.get("news_id")
    comment_content = request.json.get("comment")
    parent_id = request.json.get("parent_id", None)
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    if not all([news_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 将数据添加到评论表中，如果是回复，则有parent_id， 如果是评论，则没有parent_id
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = int(news_id)
    if parent_id:
        comment.parent_id = int(parent_id)
    comment.content = comment_content
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库连接错误")

    return jsonify(errno=RET.OK, errmsg="成功", data=comment.to_dict())


@news_blueprint.route('/comment_like', methods=["POST"])
@user_login
def comment_like():
    """评论点赞和取消功能"""

    action = request.json.get("action")
    comment_id = request.json.get("comment_id")
    news_id = request.json.get("news_id")
    user = g.user

    if not all([action, comment_id, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    if action not in ['add', 'remove']:
        return jsonify(errno=RET.PARAMERR, errmsg="action参数错误")
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 如果传入的action为add， 则将user_id和comment_id传入commentlike表中
    if action == "add":
        try:
            comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            comment.like_count += 1

    # 如果传入的action为remove， 则将user_id和comment_id从commentlike表中删除
    elif action == "remove":
        try:
            comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
        if not comment_like:
            return jsonify(errno=RET.NODATA, errmsg="以前没有收藏啊")
        comment.like_count -= 1
        db.session.delete(comment_like)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    return jsonify(errno=RET.OK, errmsg="成功")


@news_blueprint.route('/followed_user', methods=["POST"])
@user_login
def followed_user():
    """ 关注和取消关注功能 """
    user = g.user
    data_dict = request.json
    user_id = int(data_dict.get("user_id"))
    action = data_dict.get("action")

    # 对数据进行验证
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    if action not in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    author = User.query.get(user_id)

    # 处理数据
    if action == "follow":
        if author in user.authors:
            return jsonify(errno=RET.DATAEXIST, errmsg="作者已经被关注")
        user.authors.append(author)
    elif action == "unfollow":
        user.authors.remove(author)

    # 提交数据
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据存储失败")

    return jsonify(errno=RET.OK, errmsg="操作成功")











