import click

from watchlist import app, db
from watchlist.models import User, Movie


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

    user = User(name=name)
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
        user = User(username=username, name='Whxcer')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')

