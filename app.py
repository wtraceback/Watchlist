from flask import Flask, render_template, url_for, request, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
from flask_sqlalchemy import SQLAlchemy     # 导入扩展类
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import click


app = Flask(__name__)


# 在扩展类实例化之前设置好配置项
WIN = sys.platform.startswith('win')
if WIN:
    # 如果是 Windows 系统，则使用三个斜线
    prefix = 'sqlite:///'
else:
    # 否则使用四个斜线
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'


# 扩展 初始化 操作
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录.'

# 用户加载回调函数
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


# 创建数据库模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 自定义命令
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""

    if drop:
        db.drop_all()
    db.create_all()

    # 操作完成后显示提示信息
    click.echo('Initialized database.')

@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = 'Whxcer'
    movies = [
        {'title': '两杆大烟枪', 'year': '1998'},
        {'title': '偷拐抢骗', 'year': '2000'},
        {'title': '疯狂的石头', 'year': '2006'},
        {'title': '疯狂的赛车', 'year': '2009'},
        {'title': '驴得水', 'year': '2016'},
        {'title': '让子弹飞', 'year': '2010'},
        {'title': '阳光灿烂的日子', 'year': '1995'},
        {'title': '乱世佳人', 'year': '1939'},
        {'title': '七武士', 'year': '1954'},
        {'title': '罗生门', 'year': '1950'},
        {'title': '低俗小说', 'year': '1994'},
        {'title': '心迷宫', 'year': '2015'},
        {'title': '暴裂无声', 'year': '2017'},
        {'title': '可可西里', 'year': '2004'},
        {'title': '驭风男孩', 'year': '2019'},
        {'title': '流浪地球', 'year': '2019'},
    ]

    user = User.query.first()
    user.name = 'Whxcer'
    db.session.add(user)

    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')


# 模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    # 等同于 return {'user': user}
    return dict(user=user)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')

        # 验证表单数据
        if not title or not year or len(title) > 60 or len(year) > 4:
            flash('输入格式错误 -- 数据太短或是超长.')
            return redirect(url_for('index'))

        # 将表单数据保存到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('已创建一条清单.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(title) > 60 or len(year) > 4:
            flash('输入格式错误 -- 数据太短或是超长.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('该条清单更新成功.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    db.session.delete(movie)
    db.session.commit()
    flash('该条清单已删除.')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入的数据不能为空.')
            return redirect(url_for('login'))

        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('登录成功.')
            return redirect(url_for('index'))

        flash('验证失败，输入的用户名或密码错误.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('拜拜.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name =  request.form('name')

        if not name or len(name) > 20:
            flash('无效的输入.')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('用户名更改成功.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500