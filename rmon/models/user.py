from .base import BaseModel
from rmon.models.models import db
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from calendar import timegm
import jwt


class User(BaseModel):
    """用户模型
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    wx_id = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    login_at = db.Column(db.DateTime)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, passwd):
        """设置密码
        """
        self._password = generate_password_hash(passwd)

    def verify_password(self, password):
        """检查密码
        """
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, identifier, password):
        """认证用户

        Args:
                identifier(str): 用户名或邮箱
                password(str): 用户密码

        Returns:
                object: 用户对象

        Raise:
                AuthenticationError
        """
        user = cls.query.filter(
            db.or_(cls.name == identifier, cls.email == identifier)).first()
        if user is None or not user.verify_password(password):
            raise AuthenticationError(403, 'authentication failed')
        return user

    def generate_token(self):
        """生成json web token
        生成token， 有效期为1天，过期后十分钟内可以使用老token刷新获取新的token
        """
        # token过期时间，默认在一天后过期
        exp = datatime.utcnow() + timedelta(days=1)

        # token过期后十分钟内，还可以使用老token进行刷新token
        refresh_exp = timegm((exp + timedelta(seconds=60 * 10)).utctimetuple())

        payload = {
            'uid': self.id,
            'is_admin': self.is_admin,
            'exp': exp,
            'refresh_exp': refresh_exp
        }

        return jwt.encode(payload, current_app.secret_key, algorithm='HS512').decode('utf-8')

    @classmethod
    def verify_token(cls, token, verify_exp=True):
        """检查验证json web token

        Args:
                token(str): json web token
                verify_exp(bool): 是否验证token的过期时间

        Return:
                object: 返回用户对象

        Raise:
                InvalidTokenError
        """
        now = datetime.utcnow()

        if verify_exp:
            options = None
        else:
            options = {'verify_exp': False}

        try:
            payload = jwt.decode(token, current_app.secret_key, verify=True, algorithm=[
                                 'HS512'], options=options, require_exp=True)
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(403, str(e))

        # 验证token是否正确
        if any(('is_admin' not in payload, 'refresh_exp' not in payload, 'uid' not in payload)):
            raise InvalidTokenError(403, 'invalid token')

        # 如果刷新时间过期，则认为token无效
        if payload['refresh_exp'] < timegm(now.utctimetuple()):
            raise InvalidTokenError(403, 'invalid token')

        u = User.query.get(payload.get('uid'))
        if u is None:
            raise InvalidTokenError(403, 'user not exist')
        return u

    @classmethod
    def create_administrator(cls):
        """创建管理员账户

        Return：
                name(str): 管理员账户名称
                password(str): 管理员账户密码
        """
        name = 'admin'
        # 管理员账户名称默认为admin
        admin = cls.query.filter_by(name=name).first()
        if admin:
            return admin.name, ''
        password = '123456'
        admin = User(name=name, email='admin@rmon.com', is_admin=True)
        admin.password = password
        admin.save()
        return name, password

    @classmethod
    def wx_id_user(cls, wx_id):
        """根据 wx_id获取用户
        """
        return cls.query.filter_by(wx_id=wx_id).first()
