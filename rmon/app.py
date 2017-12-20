"""rmon.app
该模块主要实现来app创建函数
"""
from rmon.config import DevConfig, ProductConfig

def create_app():
	"""创建并初始化 Flask app
	"""

	#创建app对象
	app = Flask('rmon')

	#根据环境变量加载开发环境或生产环境配置
	env = os.environ.get('RMON_ENV')

	if env in ('pro', 'prod', 'product'):
		app.config.from_object(ProductConfig)
	else:
		app.config.from_object(DevConfig)

	# 从环境变量RMON_SETTINGS指定的文件中加载配置
	app.config.from_envvar('RMON_SETTINGS', slient=True)

	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	#注册Blueprint
	app.register_blueprint(api)
	