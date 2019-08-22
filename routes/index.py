import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
    current_app)
from werkzeug.datastructures import FileStorage

from config import admin_mail
from models.message import send_mail
from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import current_user, cache, new_csrf_token
from utils import log
import gevent
import time
import json

id_token = dict()


main = Blueprint('index', __name__)

"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    # t = threading.Thread()
    # t.start()
    # gevent.spawn()
    time.sleep(0.5)
    print('time type', time.sleep, gevent.sleep)
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    log('login user', u)
    if u is None:
        return redirect(url_for('.index'))
    else:
        # session 中写入 user_id
        session_id = str(uuid.uuid4())
        key = 'session_id_{}'.format(session_id)
        log('index login key <{}> user_id <{}>'.format(key, u.id))
        cache.set(key, u.id)

        redirect_to_index = redirect(url_for('topic.index'))
        response = current_app.make_response(redirect_to_index)
        response.set_cookie('session_id', value=session_id)
        # 转到 topic.index 页面
        return response


def created_topic(user_id):
    # O(n)
    ts = Topic.all(user_id=user_id)
    return ts
    #
    # k = 'created_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     ts = Topic.all(user_id=user_id)
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #     return ts


def replied_topic(user_id):
    # O(k)+O(m*n)
    rs = Reply.all(user_id=user_id)
    ts = []
    for r in rs:
        t = Topic.one(id=r.topic_id)
        if t not in ts:
            ts.append(t)
    return ts
    #
    # k = 'replied_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     Topic.select()
        #      .join(Reply, 'id', 'topic_id')
        #      .where(user_id=user_id)
        #      .all()
        # rs = Reply.all(user_id=user_id)
        # ts = []
        # for r in rs:
        #     t = Topic.one(id=r.topic_id)
        #     ts.append(t)
        #
        # v = json.dumps([t.json() for t in ts])
        # cache.set(k, v)
        #
        # return ts


@main.route('/profile')
def profile():
    print('running profile route')
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        created = created_topic(u.id)
        replied = replied_topic(u.id)
        return render_template(
            'profile.html',
            user=u,
            created=created,
            replied=replied,
        )


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    # file = request.files['avatar']
    # filename = file.filename
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    # filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    filename = str(uuid.uuid4())
    path = os.path.join('images', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/images/{}'.format(filename))

    return redirect(url_for('.profile'))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:2000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    return send_from_directory('images', filename)


@main.route('/setting')
def setting():
    u = current_user()
    token = new_csrf_token()
    board_id = 0
    return render_template('setting.html', user=u, token=token, bid=board_id)


@main.route('/setting/common_change', methods=['POST'])
def common_change():
    form = request.form
    log('form:', form)
    u = current_user()
    u.username = form['name']
    u.signature = form['signature']
    u.save()
    return redirect('/setting')


@main.route('/setting/password_change', methods=['POST'])
def password_change():
    u = current_user()
    form = request.form
    old_ps = User.salted_password(form['old_pass'])
    new_ps = User.salted_password(form['new_pass'])
    if old_ps == u.password:
        u.password = new_ps
    u.save()
    return redirect('/setting')


@main.route('/reset/send', methods=['POST'])
def reset_password():
    title = '重置密码'
    name = request.form['username']
    user = User.one(username=name)
    token = new_csrf_token()
    id_token[token] = user.id
    log('reset_token', token)
    content = 'http://localhost:4000/reset/view?token={}'.format(token)
    send_mail(
        subject=title,
        author=admin_mail,
        to=user.email,
        content=content
    )
    return redirect('/')


@main.route('/reset/view')
def reset_view():
    token = request.args['token']
    if token in id_token:
        return render_template('reset.html', token=token)
    else:
        return abort(401)


@main.route('/reset/update')
def reset_update():
    token = request.args['token']
    new_ps = request.args['password']
    if token in id_token:
        user_id = id_token[token]
        user = User.one(id=user_id)
        user.password = User.salted_password(new_ps)
        user.save()
        return redirect('/')
    else:
        return abort(401)
