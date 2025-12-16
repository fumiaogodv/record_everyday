from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
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

