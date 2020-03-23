from flask import (
    render_template,
    request,
    redirect,
    Blueprint,
)
from models.user import User
from routes import current_user, new_csrf_token
from utils import log


main = Blueprint('setting', __name__)


@main.route("/")
def index():
    u = current_user()
    token = new_csrf_token(u)
    board_id = 0
    return render_template('setting.html', user=u, token=token, bid=board_id)


@main.route('/common_change', methods=['POST'])
def common_change():
    form = request.form
    log('form:', form)
    u = current_user()
    u.username = form['name']
    u.signature = form['signature']
    u.save()
    return redirect('/setting')


@main.route('/password_change', methods=['POST'])
def password_change():
    u = current_user()
    form = request.form
    old_ps = User.salted_password(form['old_pass'])
    new_ps = User.salted_password(form['new_pass'])
    if old_ps == u.password:
        u.password = new_ps
    u.save()
    return redirect('/setting')
