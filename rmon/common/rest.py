"""rmon.common.rest
"""
from collections import Mapping
from flask import request, make_response
from flask.json import dumps
from flask.views import MethodView


class RestException(Exception):
    """异常基类
    """

    def __init__(self, code, message):
        """初始化异常

        Args:
                code(int): http状态码
                message(str): 错误信息
        """
        self.code = code
        self.message = message
        super().__init__()


class RestView(MethodView):
    """自定义View类

    json序列化，异常处理，装饰器支持
    """
    content_type = 'application/json; charset=utf-8'
    method_decorators = []

    def handler_error(self, exception):
        """处理异常
        """
        data = {
            'ok': False,
            'message': exception.message
        }

        result = dumps(data) + '\n'
        resp = make_response(result, exception.code)
        resp.headers['Content-Type'] = self.content_type
        return resp

    def dispatch_request(self, *args, **kwargs):
        """重写父类方法，支持数据自动序列化
        """

        # 获取对应于 HTTP 请求方式的视图方法(rmon.views里的视图控制器类中的方法)
        method = getattr(self, request.method.lower(), None)

        if method is None and request.method == 'HEAD':  # 如果请求方法为HEAD，而且没有对应的视图方法
        	#那么就用视图控制器类中的get方法来返回
        	method = getattr(self, 'get', None)

        # 如果仍然没法获取到视图方法，就抛出异常，打印request请求的方法
        assert method is not None, 'Unimplemented method %r' %request.method


