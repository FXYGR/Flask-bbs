import uuid
from functools import wraps

import redis
from flask import session, request, abort

from models.user import User
from utils import log

cache = redis.StrictRedis()


def current_user():
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        # s = Session.one_for_session_id(session_id=session_id)
        key = 'session_id_{}'.format(session_id)
        user_id = int(cache.get(key).decode())
        log('current_user key <{}> user_id <{}>'.format(key, user_id))
        u = User.one(id=user_id)
        return u
    else:
        return None


# csrf_tokens = dict()


# def csrf_required(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         token = request.args['token']
#         u = current_user()
#         if token in csrf_tokens and csrf_tokens[token] == u.id:
#             csrf_tokens.pop(token)
#             return f(*args, **kwargs)
#         else:
#             abort(401)
#
#     return wrapper
#
#
# def new_csrf_token():
#     u = current_user()
#     token = str(uuid.uuid4())
#     csrf_tokens[token] = u.id
#     return token


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        print('token', token)
        u = current_user()
        k = 'csrf_token_{}'.format(token)
        if cache.exists(k):
            v = cache.get(k)
            log('csrf_token', v,)
            if v == u.id:
                cache.delete(k)
                return f(*args, **kwargs)
            else:
                log('v 的格式不对')
                abort(401)
        else:
            log('csrf not in cache')
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    k = 'csrf_token_{}'.format(token)
    v = u.id
    cache.set(k, v)
    return token


