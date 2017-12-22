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
        assert resp.headers['Content-Type'] = 'application/json;charset=utf-8'
        # 访问成功后返回状态码 200 OK
        assert resp.status_code = 200

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
        """测试创建Redis服务器成功"""
        # TUDO
        pass

    def test_create_server_failed_with_invalid_host(self, db, client):
        """无效的服务器地址导致创建Redis服务器失败"""
        pass

    def test_create_server_failed_with_duplciate_server(self, server, client):
        """创建重复的服务器时将失败"""
        pass


class TestServerDetail:
    """测试Redis服务器详情API
    """
    endpoint = 'api.server_detail'

    def test_get_server_success(self, server, client):
        """测试获取Redis服务器详情
        """
        pass

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
