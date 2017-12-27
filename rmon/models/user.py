class User(BaseModel):
	"""用户模型
	"""
	def __init__(self, arg):
		super(User, self).__init__()
		self.arg = arg
		