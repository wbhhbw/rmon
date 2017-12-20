from rmon.models import Server

class TestServer:
	"""测试Server相关功能
	"""

	def test_save(self, db):
		"""测试Server.save 保存服务器方法
		"""

		# 初始状态下，数据库没有保存任何Redis服务器，所以数量为0
		assert Server.query.count() == 0
		# 创建server对象
		server= Server(name='test', host='127.0.0.1')
		# 保存到数据库中
		server.save()
		# 此时数据库中Redis服务器数量变为1
		assert Server.query.count() == 1
		# 并且查询到的对象就是刚刚存入的对象
		assert Server.query.first() == server

	def test_delete(self, db, server):
		"""测试 Server.delete 删除服务器方法
		"""
		# 传入server依赖后，数据库中有一条记录
		assert Server.query.count() == 1
		# 测试删除功能
		server.delete()
		# 删除后为记录为0
		assert Server.query.count() == 0



