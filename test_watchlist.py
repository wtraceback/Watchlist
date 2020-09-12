import unittest

from watchlist import app, db
from watchlist.models import User, Movie
from watchlist.commands import forge, initdb


class Watchlist_TestCase(unittest.TestCase):

    def setUp(self):
        # 更新配置
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )

        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户和一个电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='千钧一发', year='1997')

        # 使用 add_all() 方法一次添加多个模型类实例，传入列表
        db.session.add_all([user, movie])
        db.session.commit()

        # 创建 测试客户端：模拟客户端请求
        # 创建 测试命令运行器：触发自定义命令
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        # 删除 数据库会话 和 数据库表
        db.session.remove()
        db.drop_all()

    def test_app_exist(self):
        """测试程序实例是否存在"""
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        """测试程序是否处于测试模式"""
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        """测试 404 页面"""
        # 调用这类方法返回包含响应数据的响应对象
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)

        self.assertIn('Page Not Found - 404', data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        """测试主页"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)

        self.assertIn('Test 的观影清单', data)
        self.assertIn('千钧一发', data)
        self.assertEqual(response.status_code, 200)

    def login(self):
        """辅助方法，用于登录用户"""
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    def test_create_item(self):
        """测试创建条目"""
        self.login()

        # 测试创建条目操作
        response = self.client.post('/', data=dict(
            title='千钧一发2',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertIn('已创建一条清单', data)
        self.assertIn('千钧一发2', data)

        # 测试创建条目操作，但电影标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('已创建一条清单', data)
        self.assertIn('输入格式错误 -- 数据太短或是超长', data)

        # 测试创建条目操作，但电影年份为空
        response = self.client.post('/', data=dict(
            title='千钧一发2',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('已创建一条清单', data)
        self.assertIn('输入格式错误 -- 数据太短或是超长', data)

    def test_update_item(self):
        """测试更新条目"""
        self.login()

        # 测试到达更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)

        self.assertIn('编辑', data)
        self.assertIn('千钧一发', data)
        self.assertIn('1997', data)

        # 测试更新电影条目操作
        response = self.client.post('/movie/edit/1', data=dict(
            title='千钧一发3',
            year='2025'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertIn('该条清单更新成功', data)
        self.assertIn('千钧一发3', data)

        # 测试更新电影条目，但电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2025'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('该条清单更新成功', data)
        self.assertIn('输入格式错误 -- 数据太短或是超长', data)

        # 测试更新电影条目，但电影年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='千钧一发6',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('该条清单更新成功', data)
        self.assertNotIn('千钧一发6', data)
        self.assertIn('输入格式错误 -- 数据太短或是超长', data)

    def test_delete_item(self):
        """测试删除条目"""
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertIn('该条清单已删除', data)
        self.assertNotIn('千钧一发3', data)

    def test_login_protect(self):
        """测试登录保护"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('登出', data)
        self.assertNotIn('设置', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('删除', data)
        self.assertNotIn('编辑', data)

    def test_login(self):
        """测试登录"""
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertIn('登录成功', data)
        self.assertIn('登出', data)
        self.assertIn('设置', data)
        self.assertIn('删除', data)
        self.assertIn('编辑', data)
        self.assertIn('<form method="post">', data)

        # 测试使用错误的密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('登录成功', data)
        self.assertIn('验证失败，输入的用户名或密码错误', data)

        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('登录成功', data)
        self.assertIn('验证失败，输入的用户名或密码错误', data)

        # 测试使用空的用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('登录成功', data)
        self.assertIn('输入的数据不能为空', data)

        # 测试使用空的密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('登录成功', data)
        self.assertIn('输入的数据不能为空', data)

    def test_logout(self):
        """测试登出"""
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('拜拜', data)
        self.assertNotIn('登出', data)
        self.assertNotIn('设置', data)
        self.assertNotIn('删除', data)
        self.assertNotIn('编辑', data)
        self.assertNotIn('<form method="post">', data)

    def test_settings(self):
        """测试设置"""
        self.login()

        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)

        self.assertIn('设置', data)
        self.assertIn('你的名字', data)

        # 测试更新设置
        response = self.client.post('/settings', data=dict(
            name='Whxcer',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertIn('用户名更改成功', data)
        self.assertIn('Whxcer', data)

        # 测试更新设置，名称为空
        response = self.client.post('/settings', data=dict(
            name='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)

        self.assertNotIn('用户名更改成功', data)
        self.assertIn('无效的输入', data)


    def test_forge_command(self):
        """测试虚拟数据"""
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_initdb_command(self):
        """测试初始化数据库"""
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    def test_admin_command(self):
        """测试生成管理员账户"""
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'whxcer', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'whxcer')
        self.assertTrue(User.query.first().validate_password('123'))

    def test_admin_update(self):
        """测试更新管理员账户"""
        result = self.runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()
