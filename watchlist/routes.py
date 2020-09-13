from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie, Message


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
            flash('输入格式错误 -- 数据太短或是超长')
            return redirect(url_for('index'))

        # 将表单数据保存到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('已创建一条清单')
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
            flash('输入格式错误 -- 数据太短或是超长')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('该条清单更新成功')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    db.session.delete(movie)
    db.session.commit()
    flash('该条清单已删除')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入的数据不能为空')
            return redirect(url_for('login'))

        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('登录成功')
            return redirect(url_for('index'))

        flash('验证失败，输入的用户名或密码错误')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('拜拜')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('无效的输入')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('用户名更改成功')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/guestbook', methods=['get', 'post'])
def guestbook():
    if request.method == 'POST':
        name = request.form['name']
        body = request.form['body']

        if not name or not body or len(name) > 20 or len(body) > 200:
            flash('输入格式错误 -- 数据太短或是超长')
            return redirect(url_for('guestbook'))

        # 将表单数据保存到数据库
        message = Message(name=name, body=body)
        db.session.add(message)
        db.session.commit()
        flash('您的消息已发送给全世界！')
        return redirect(url_for('guestbook'))

    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('guestbook.html', messages=messages)