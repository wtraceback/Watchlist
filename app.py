from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
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

    return render_template('index.html', name=name, movies=movies)