import functools
import uuid
import redis

from functools import wraps
from flask import request, abort, url_for, redirect
from models.user import User
from utils import log

cache = redis.StrictRedis()


def login_required(route_function):
    """
    这个函数看起来非常绕，所以你不懂也没关系
    就直接拿来复制粘贴就好了
    """

    @functools.wraps(route_function)
    def f():
        log('login_required')
        u = current_user()
        if u is None:
            log('游客用户')
            return redirect(url_for('index.index'))
        else:
            log('登录用户', route_function)
            return route_function()

    return f


def current_user():
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        key = 'session_id_{}'.format(session_id)
        user_id = cache.get(key)
        log('current_user key <{}> user_id <{}>'.format(key, user_id))
        u = User.one(id=user_id)
        return u
    else:
        return None


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        u = current_user()
        key = 'csrf_token_{}'.format(token)
        if cache.exists(key) and int(cache.get(key)) == u.id:
            cache.delete(key)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token(user):
    token = str(uuid.uuid4())
    k = 'csrf_token_{}'.format(token)
    v = user.id
    cache.set(k, v)
    return token


