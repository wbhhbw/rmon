from functools import wraps
from flask import g
from rmon.common.rest import RestException
from flask import request
from rmon.common.errors import AuthenticationError
from rmon.models.user import User


class ObjectMustBeExist:
    """该装饰器确保操作的对象必须存在
    """

    def __init__(self, object_class):
        """
        Args:
                object_class(class): 数据库对象
        """
        self.object_class = object_class

    def __call__(self, func):  # __call__方法可以让一个类的实例(如obj)，像函数那样调用obj(func)
        """装饰器实现
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Args:
                object_id(int): SQLAlchemy object id
            """
            object_id = kwargs.get('object_id')
            if object_id is None:
                raise RestException(404, 'object not exist')

            obj = self.object_class.query.get(object_id)
            if obj is None:
                raise RestException(404, 'object not exist')

            g.instance = obj
            return func(*args, **kwargs)

        return wrapper


class TokenAuthenticate:
    """通过jwt认证用户

    验证HTTP Authorization 头所包含的 token
    """

    def __init__(self, admin=True):
        """
        Args: 
            admin(bool): 是否需要验证管理员权限
        """
        self.admin = admin

    def __call__(self, func):
        """装饰器实现
        """
        @wraps(func)
        def wrapper(*args, **kwargs):

            pack = request.headers.get('Authorization', None)
            if pack is None:
                raise AuthorizationError(401, 'token not found')
            parts = pack.split()  # 默认按照空格分隔
            # Authorization 头部值必须为 'jwt <token_value>' 这种形式
            if parts[0].lower() != 'jwt':
                raise AuthorizationError(401, 'invalid token headers')
            elif len(parts) == 1:
                raise AuthorizationError(401, 'token missing')
            elif len(parts) > 2:
                raise AuthorizationError(401, 'invalid token')
            token = parts[1]
            user = User.verify_token(token)

            # 如果需要验证是否是管理员
            if self.admin and not user.is_admin:
                raise AuthorizationError(403, 'no permission')

            # 将当前用户存入到 g 对象中
            g.user = user
            return func(*args, **kwargs)
        return wrapper
