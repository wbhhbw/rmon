"""app.py
应用程序入口文件
"""
from rmon.app import create_app
from rmon.models import db

app = create_app()

@app.cli.command()
def init_db():
	"""初始化数据库
	"""
	print("sqllite3 database file is %s" % app.config['SQLALCHEMY_DATABASE_URI'])
	db.create_all()