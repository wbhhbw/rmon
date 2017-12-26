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
        assert db.session.query(Server).count() == 0

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

        # 返回的结果为 json格式
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
        # 发起get请求获取服务器详情, 该数据库模型id不存在
        resp = client.get(url_for(self.endpoint, object_id=3))

        # 返回的结果为 json格式
        assert resp.headers[
            'Content-Type'] == 'application/json; charset=utf-8'

        # 访问失败，状态码为404
        assert resp.status_code == 404

        # 验证相应信息
        assert resp.json['ok'] == False
        assert resp.json['message'] == 'object not exist'

    def test_update_server_success(self, server, client):
        """更新Redis服务器成功
        """
        # 由于当前测试环境中只有一个 Redis 服务器，所以查询服务器的个数为1
        assert Server.query.first() == server

        data = {
            'name': server.name,  # 更新server记录，这个字段必须加上，否则无法判断是否重名
            'description': 'I have changed the description'  # 更新描述
        }
        headers = {
            'Content-Type': 'application/json'
        }

        # HTTP put方法更新同名服务器
        resp = client.put(url_for(self.endpoint, object_id=server.id),
                          data=json.dumps(data), headers=headers)

        # 访问成功后返回状态码 200 OK
        assert resp.status_code == 200

        # 验证相应信息
        assert resp.json['ok'] == True

        # 更新操作不改变服务器列表，查询服务器数量仍为1
        assert Server.query.count() == 1

        # 验证数据库中字段已经更改
        server_new = Server.query.first()
        assert server_new.description == 'I have changed the description'
        assert server_new.id == server.id
        assert server_new.name == server.name
        assert server_new.host == server.host

    def test_update_server_failed_with_duplicate_server(self, server, client):
        """更新服务器名称为其他同名服务器名称时失败:
           假设要更新server的name字段，但是更改的时候改成了和second_server 同名报错
        """

        # 数据库中有一条记录
        assert Server.query.first() == server

        # 创建second_server
        second_server = Server(name='second_server',
                               host='192.168.0.1', port=6379)
        second_server.save()

        # 数据库中有两条记录
        assert Server.query.count() == 2

        data = {
            'name': second_server.name,  # 更新名字，与另一记录重复
            'description': 'I have changed the description'  # 更新描述
        }
        headers = {
            'Content-Type': 'application/json'
        }

        # HTTP put方法更新sever服务器，并与second_server同名
        resp = client.put(url_for(self.endpoint, object_id=server.id),
                          data=json.dumps(data), headers=headers)

        # 更新失败，状态码为400
        assert resp.status_code == 400

        # 验证错误信息
        assert resp.json == {'ok': False,
                             'message': 'Redis server alredy exist'}

    def test_delete_success(self, server, client):
        """删除Redis服务器成功
        """
        # 数据库中有一条记录
        assert Server.query.first() == server

        # HTTP delete方法删除server服务器
        resp = client.delete(url_for(self.endpoint, object_id=server.id))

        # 访问成功后返回状态码 204
        assert resp.status_code == 204

        # 数据库中没有记录
        assert Server.query.count() == 0

    def test_delete_failed_with_host_not_exist(self, db, client):
        """删除不存在的Redis服务器失败
        """
        # 数据库中没有记录
        assert Server.query.count() == 0

        # HTTP delete方法删除server服务器
        resp = client.delete(url_for(self.endpoint, object_id=10))

        # 对象不存在，状态码为404
        assert resp.status_code == 404

        # 验证错误信息
        assert resp.json == {'ok': False,
                             'message': 'object not exist'}

        # 数据库中没有记录
        assert Server.query.count() == 0
