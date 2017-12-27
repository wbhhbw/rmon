from flask import request, g

from rmon.common.rest import RestView
from rmon.views.decorators import ObjectMustBeExist, TokenAuthenticate
from rmon.models.server import Server, ServerSchema


class ServerList(RestView):
    """Redis服务器列表"""

    def get(self):
        """获取Redis列表"""
        servers = Server.query.all()
        return ServerSchema().dump(servers, many=True).data

    def post(self):
        """创建Redis服务器
        """
        data = request.get_json()
        server, errors = ServerSchema().load(data)
        if errors:
            return errors, 400
        server.ping()
        server.save()
        return {'ok': True}, 201


class ServerDetail(RestView):
    """Redis 服务器详情
    """
    method_decorators = (ObjectMustBeExist(Server), TokenAuthenticate(server))  # 装饰器类实例化传入Server对象

    def get(self, object_id):
        """获取服务器详情
        """
        data, _ = ServerSchema().dump(g.instance)
        return data

    def put(self, object_id):
        """更新服务器
        """
        schema = ServerSchema(
            context={'instance': g.instance})  # g.instance 来自于装饰器的get(object_id)
        data = request.get_json()
        server, errors = schema.load(data, partial=True)
        if errors:
            return errors, 400
        server.save()
        return {'ok': True}

    def delete(self, object_id):
        """删除服务器
        """
        g.instance.delete()
        return {'ok': True}, 204

class ServerMetrics(RestView):
    """服务器监控信息
    """
    method_decorators = (ObjectMustBeExist(Server),)  # 装饰器类实例化传入Server对象, 该装饰其保证对象存在

    def get(self, object_id):
        """获取服务器监控信息
        """
        return g.instance.get_metrics()