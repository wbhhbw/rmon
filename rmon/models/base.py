from datetime import datetime
from rmon.models import db


class BaseModel(db.model):
    """模型抽象基础类
    通过设置__abstract__属性，成为SQLAlchemy 抽象基类， 不再映射到数据库中
    """
    __abstract__ = True

    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
    	try:
    		identifier = self.name
    	except AttributeError:
    		identifier = self.id
    	return "<{} {}>".format(self.__class__.__name__, identifier) # 结果形如<类名 name>

    def save(self):
        """保存到数据库中
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """从数据库中删除
        """
        db.session.delete(self)
        db.session.commit()

