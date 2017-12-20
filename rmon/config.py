"""rmon.config
"""
import os

class DevConfig:
	"""开发环境配置
	"""
	
	DEBUG = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_DATABASE_URI = 'sqlite://'
	TEMPLATES_AUTO_RELOAD = True

class ProductConfig(DevConfig):
	"""生产环境配置
	"""
	
	DEBUG = False

	path = os.path.join(os.getcwd(), 'rmon.db').replace('\\', '/')
	SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % path
		
