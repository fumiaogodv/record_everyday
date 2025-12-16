from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ##################################################################
#  关键修改部分：添加一个中间件来处理 URL 前缀
# ##################################################################
class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        # 如果请求路径以指定的前缀开头，则移除前缀
        # 例如，将 /hello/wuziqi 修改为 /wuziqi
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            # 如果不匹配前缀，直接返回 404
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This URL does not belong to the app.".encode()]

# 将你的 Flask 应用包装在这个中间件中
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/hello')
# ##################################################################



app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'your-secret-key'

db = SQLAlchemy()
db.init_app(app)


# 数据库模型
class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.String(10), nullable=False)
    messages = db.Column(db.String(100), nullable=False)


# 初始化数据库
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template("index.html")


@app.route('/read_page', methods=['GET'])
def read():
    # 从数据库获取所有日记，按时间倒序排列
    diaries = Diary.query.order_by(Diary.id.desc()).all()
    return render_template('read.html', diaries=diaries)


@app.route('/write_page', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        try:
            date = request.form.get('date')
            content = request.form.get('content')

            print(f"收到表单数据: date={date}, content={content}")

            if not date or not content:
                return "时间或内容不能为空，请重新填写", 400

            # 创建并保存日记
            new_diary = Diary(date_time=date, messages=content)
            db.session.add(new_diary)
            db.session.commit()

            print("数据库插入成功")
            return redirect(url_for('main'))

        except Exception as e:
            db.session.rollback()
            print(f"数据库插入失败: {str(e)}")
            return f"数据库插入失败: {str(e)}", 500
    else:
        return render_template('write.html')


if __name__ == "__main__":
    print("启动Flask应用...")
    app.run(debug=True)
