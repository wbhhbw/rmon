import json
from flask import url_for

from rmon.models import Server


class TestServerList:
    """测试Redis服务器列表API"""

    endpoint = 'api.server_list'

    def test_get_servers(self, server, client):
        """获取Redis服务器列表	"""
        resp = client.get(url_for(self.endpoint))  # client用于发起请求

        # RestView 视图基类会设置 HTTP 头部 Content-Type 为 json
        assert resp.headers[
            'Content-Type'] == 'application/json; charset=utf-8'
        # 访问成功后返回状态码 200 OK
        assert resp.status_code == 200

        servers = resp.json

        # 由于当前测试环境中只有一个 Redis 服务器，所以返回的数量为 1
        assert len(servers) == 1
        h = servers[0]
        assert h['name'] == server.name
        assert h['description'] == server.description
        assert h['host'] == server.host
        assert h['port'] == server.port
        assert 'updated_at' in h
        assert 'created_at' in h

    def test_create_server_success(self, db, client):
        """测试创建Redis服务器成功
        """

        # 创建前，数据库中没有记录
        assert Server.query.count() == 0
        # 构建post请求，创建服务器
        data = {
            'name': 'test',
            'description': 'this is a test record',
            'host': '127.0.0.1'
        }
        headers = {
            'Content-Type': 'application/json'
        }
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data), headers=headers)

        # 创建成功返回状态码201
        assert resp.status_code == 201
        assert resp.json == {'ok': True}

        # 写入数据库成功
        assert Server.query.count() == 1
        server = Server.query.first()
        assert server is not None
        for key in data:
            assert getattr(server, key) == data[key]

    def test_create_server_failed_with_invalid_host(self, db, client):
        """无效的服务器地址导致创建Redis服务器失败"""

        # 创建前，数据库中没有记录
        assert Server.query.count() == 0

        # 传入无效的服务器地址
        data = {
            'name': 'test',
            'description': 'this is a test record',
            'host': '127.0.0.2'   # 无效服务器地址
        }
        headers = {
            'Content-Type': 'application/json'
        }
        # 发起POST请求，创建服务器
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data), headers=headers)

        # 创建失败返回状态码201
        assert resp.status_code == 400
        # 验证相应信息
        assert resp.json['ok'] == False
        assert resp.json['message'] is not None

        # 创建失败，数据库中依然没有记录
        assert Server.query.count() == 0

    def test_create_server_failed_with_duplciate_server(self, server, client):
        """创建同名的服务器时将失败
        """

        # 由于当前测试环境中只有一个 Redis 服务器，所以查询服务器的个数为1
        assert Server.query.count() == 1

        data = {
            'name': server.name,  # 重复地址
            'description': 'this is a another test record',
            'host': server.host
        }
        headers = {
            'Content-Type': 'application/json'
        }

        # Post方法创建同名服务器
        resp = client.post(url_for(self.endpoint),
                           data=json.dumps(data), headers=headers)

        # 创建失败返回状态码400
        assert resp.status_code == 400

        # 验证相应信息
        assert resp.json['ok'] == False
        assert resp.json['message'] == 'Redis server alredy exist'

        # 创建失败，数据库中仍然只有一条记录
        assert Server.query.count() == 1


class TestServerDetail:
    """测试Redis服务器详情API
    """
    endpoint = 'api.server_detail'

    def test_get_server_success(self, server, client):
        """测试获取Redis服务器详情
        """
        # 由于当前测试环境中只有一个 Redis 服务器，所以查询服务器的个数为1
        assert Server.query.count() == 1

        # 发起get请求获取服务器详情, 注意此处的url_for函数要传入两个参数
        resp = client.get(url_for(self.endpoint, object_id=server.id))

        # 确保RestView 视图基类已经设置 HTTP 头部 Content-Type 正确的设置为 json
        assert resp.headers[
            'Content-Type'] == 'application/json; charset=utf-8'

        # 访问成功后返回状态码 200 OK
        assert resp.status_code == 200

        h = resp.json
        assert h['name'] == server.name
        assert h['description'] == server.description
        assert h['host'] == server.host
        assert h['port'] == server.port
        assert 'updated_at' in h
        assert 'created_at' in h

        # 查询操作不改变服务器列表，查询服务器仍为server
        assert Server.query.first() == server


    def test_get_server_failed(self, db, client):
        """获取不存在的Redis服务器详情失败
        """
        pass

    def test_update_server_success(self, server, client):
        """更新Redis服务器成功
        """
        pass

    def test_update_server_failed_with_duplicate_server(self, server, client):
        """更新服务器名称为其他同名服务器名称时失败
        """
        pass

    def test_delete_success(self, server, client):
        """删除Redis服务器成功
        """
        pass

    def test_delete_failed_with_host_not_exist(self, db, client):
        """删除不存在的Redis服务器失败
        """
        pass
