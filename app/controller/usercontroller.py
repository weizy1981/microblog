from app.models.models import Users, Posts
from app.models import session
from datetime import datetime
from app.controller.full_text_search import create_index

class UserController:
    def query(self, username, password):
        user = session.query(Users).filter_by(username=username, password=password).first()
        return user

    def query_byId(self, user_id):
        user = session.query(Users).filter_by(id=user_id).first()
        return user

    def query_byname(self, username):
        user = session.query(Users).filter_by(username=username).first()
        return user

    def update(self, user):
        session.add(user)
        session.commit()

    def add(self, username, password, nickname, description):
        user = Users()
        user.username = username
        user.password = password
        user.nickname = nickname
        user.description = description
        user.email = ''
        user.imgpath = 'default.jpg'

        # 保存DB
        session.add(user)
        session.commit()
        # 关注自己
        user.follow(user)
        session.add(user)
        session.commit()
        return user

    # 增加Post
    def addpost(self, user_id, nickname, post_body):
        post = Posts()
        post.user_id = user_id
        post.body = post_body
        post.timestamp = datetime.utcnow()
        session.add(post)
        session.commit()
        # 建立全文检索索引
        create_index(user_id=user_id, post_id=post.id, nickname=nickname, post_body=post_body)
        return post

    # Post检索
    def search_posts(self, post_ids):
        posts = session.query(Posts).filter(Posts.id.in_(other=post_ids)).order_by(Posts.timestamp.desc()).all()
        return posts

    def search_post_byId(self, id):
        post = session.query(Posts).filter_by(id=id).first()
        return post

    def delete_post(self, post):
        session.delete(post)
        session.commit()
