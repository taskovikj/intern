from flask import Blueprint, render_template, request
import os
from .tasks import make_file, complex_task


bp = Blueprint("views", __name__)

@bp.route("/")
def index():
    return "Hello!!!"

@bp.route("/<string:fname>/<string:content>")
def makefile(fname, content):
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    make_file.delay(fpath, content)
    return f"Find your file @ <code>{fpath}</code>"



@bp.route('/test/', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        hello = complex_task.delay('task_completed')
        print (hello)
        return render_template('test.html')
    


