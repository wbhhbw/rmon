from flask import request, g

from rmon.common.rest import RestView
from rmon.models import Server, ServerSchema

class ServerList(RestView):
	"""Redis服务器列表"""
	def get(self):
		"""获取Redis列表"""
		servers = Server.query.all()
		return ServerSchema().dump(servers, many=True).data

	def post(self):
		"""创建Redis服务器
		"""
		data = request.get_json()
		server, errors = ServerSchema().load(data)
		if errors:
			return errors, 400
		server.ping()
		server.save()
		return {'ok': True}, 201