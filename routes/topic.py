from flask import (
    render_template,
    Blueprint,
)

from routes import *
from utils import log
from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)


@main.route("/")
def index():
    u = current_user()
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    token = new_csrf_token(u)
    bs = Board.all()
    return render_template("topic/index.html", ms=ms, token=token, bs=bs, bid=board_id, user=u)


@main.route('/<int:id>')
def detail(id):
    board_id = int(request.args.get('board_id', -1))
    board = Board.one(id=board_id)
    log("topic detail:", board_id, board)
    m = Topic.get(id)

    return render_template("topic/detail.html", topic=m, board=board)


@main.route("/delete")
@csrf_required
@login_required
def delete():
    u = current_user()
    id = int(request.args.get('id'))

    Topic.delete(id)
    return redirect(url_for('.index'))


@main.route("/new")
@login_required
def new():
    u = current_user()
    board_id = int(request.args.get('board_id'))
    bs = Board.all()
    token = new_csrf_token(u)
    return render_template("topic/new.html", bs=bs, token=token, bid=board_id)


@main.route("/add", methods=["POST"])
@csrf_required
def add():
    form = request.form.to_dict()
    u = current_user()
    Topic.new(form, user_id=u.id)
    return redirect(url_for('.index'))
