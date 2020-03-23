
from flask import (
    render_template,
    request,
    redirect,
    Blueprint,
    abort,
)

from config import admin_mail
from models.message import send_mail
from models.user import User
from routes import cache, new_csrf_token
from utils import log


main = Blueprint('reset', __name__)


@main.route('/')
def index():
    return render_template('send.html')


@main.route('/send', methods=['POST'])
def reset_password():
    email = request.form["email"]
    name = request.form["username"]
    title = '重置密码'
    user = User.one(email=email)
    if user is not None and name == user.username:
        token = new_csrf_token(user)
        log('reset_token', token)
        content = 'http://129.28.170.70/reset/view?token={}'.format(token)
        send_mail(
            subject=title,
            author=admin_mail,
            to=user.email,
            content=content
        )
        return redirect('/')
    else:
        message = "用户名与 Email 不匹配"
        return render_template('send.html', message=message)


@main.route('/view')
def reset_view():
    token = request.args["token"]
    key = "csrf_token_{}".format(token)
    if cache.exists(key):
        user_id = cache.get(key)
        cache.delete(key)
        user = User.one(id=user_id)
        token = new_csrf_token(user)
        return render_template('reset.html', token=token, user=user)
    else:
        return abort(401)


@main.route('/update', methods=['POST'])
def update():
    token = request.args["token"]
    key = "csrf_token_{}".format(token)
    username = request.form["username"]
    user = User.one(username=username)
    log("reset update:", user.id, cache.get(key))
    new_ps = request.form['password']
    if cache.exists(key) and int(cache.get(key)) == user.id:
        user.password = User.salted_password(new_ps)
        user.save()
        return redirect('/')
    else:
        return abort(401)
