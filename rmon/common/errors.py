class RestError(Exception):
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


class RedisConnectError(RestError):
    pass


class InvalidTokenError(RestError):
    pass


class AuthenticationError(RestError):
    pass
