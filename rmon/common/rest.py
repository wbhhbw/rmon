"""rmon.common.rest
"""
from collections import Mapping
from flask import request, make_response
from flask.json import dumps
from flask.views import MethodView
from rmon.common.errors import RestError

from werkzeug.wrappers import Response


class RestView(MethodView):
    """自定义View类，所有API均继承自该类

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
            # 那么就用视图控制器类中的get方法来返回
            method = getattr(self, 'get', None)

        # 如果仍然没法获取到视图方法，就抛出异常，打印request请求的方法
        assert method is not None, 'Unimplemented method %r' % request.method

        # HTTP 请求方法定义了不同的装饰器
        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        # 首先执行装饰器函数,如果decorators为[],那么这段代码什么也不做，method还是原来的方法
        for decorator in decorators:
            method = decorator(method)

        try:
            resp = method(*args, **kwargs)
        except RestError as e:
            resp = self.handler_error(e)

        # 如果返回结果已经是HTTP响应，那么直接返回
        if isinstance(resp, Response):
            return resp

        # 如果不是，那么需要解析视图函数的返回值
        data, code, headers = RestView.unpack(resp)

        # 处理错误，HTTP 状态码大于等于 400 时认为是错误
        # 返回的错误类似于 {'name': ['redis server already exist']} 将其调整为
        # {'ok': False, 'message': 'redis server already exist'}
        if code >= 400 and isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list) and len(data[key]) > 0:
                    message = data[key][0]
                else:
                    message = data[key]
            data = {'ok': False, 'message': message}

        # 序列化数据
        result = dumps(data) + '\n'
        # 生成HTTP响应
        response = make_response(result, code)
        response.headers.extend(headers)

        # 设置响应头部为 application/json
        response.headers['Content-Type'] = self.content_type
        return response

    @staticmethod
    def unpack(value):
        """解析视图方法返回值，视图方法的三个返回值分别为：响应字符串， 状态码，和由headers组成的字典

        """
        headers = {}
        # 返回值只有响应字符串时，其类型不是tuple
        if not isinstance(value, tuple):
            return value, 200, {}
        if len(value) == 3:
            data, code, headers = value
        elif len(value) == 2:
            data, code = value
        return data, code, headers
