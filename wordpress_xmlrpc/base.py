import xmlrpclib
import collections, types

class Client(object):
	"""
	Connection to a WordPress XML-RPC API endpoint.

	To execute XML-RPC methods, pass an instance of an
	`XmlrpcMethod`-derived class to `Client`'s `call` method.
	"""
	def __init__(self, url, username, password, blog_id=0):
		self.url = url
		self.username = username
		self.password = password
		self.blog_id = blog_id

		self.server = xmlrpclib.ServerProxy(url, use_datetime=True)
		self.supported_methods = self.server.mt.supportedMethods()

	def call(self, method):
		assert (method.method_name in self.supported_methods)
		server_method = getattr(self.server, method.method_name)
		args = method.get_args(self)
		# print method.method_name, args
		raw_result = server_method(*args)
		return method.process_result(raw_result)

class XmlrpcMethod(object):
	"""
	Base class for XML-RPC methods.

	Child classes can override methods and properties to customize behavior.
	"""
	method_name = None			# XML-RPC method name (e.g., 'wp.getUserInfo')
	method_args = None			# Tuple of method-specific parameters
	args_start_position = 0		# If greater than zero, prepends the XML-RPC argument list with this number of dummy values
	default_args_position = 0	# The index in the `method_args` list at which the default arguments should be inserted.
	results_class = None		# Python class which will convert an XML-RPC response dict into an object

	def __init__(self, *args):
		if self.method_args:
			if len(args) != len(self.method_args):
				raise Exception, "Invalid number of parameters to %s" % self.method_name

			for i, arg_name in enumerate(self.method_args):
				setattr(self, arg_name, args[i])

	def default_args(self, client):
		"""
		Builds set of method-non-specific arguments.
		"""
		return tuple()

	def get_args(self, client):
		"""
		Builds final set of XML-RPC method arguments based on
		the method's arguments, any default arguments, and their
		defined respective ordering.
		"""
		default_args = self.default_args(client)

		if self.method_args:
			args = tuple(getattr(self, arg) for arg in self.method_args)
			args = args[:self.default_args_position] + default_args + args[self.default_args_position:]
		else:
			args = default_args

		return ((0,)*self.args_start_position) + args

	def process_result(self, raw_result):
		"""
		Performs actions on the raw result from the XML-RPC response.

		If a `results_class` is defined, the response will be converted
		into one or more object instances of that class.
		"""
		if self.results_class and raw_result:
			if isinstance(raw_result, types.DictType):
				return self.results_class(raw_result)
			elif isinstance(raw_result, collections.Iterable):
				return [self.results_class(result) for result in raw_result]

		return raw_result

class AnonymousMethod(XmlrpcMethod):
	"""
	An XML-RPC method for which no authentication is required.
	"""
	pass

class AuthenticatedMethod(XmlrpcMethod):
	"""
	An XML-RPC method for which user authentication is required.

	Username and password details will be passed from the `Client`
	instance to the method call. 

	By default, the `Client`-defined blog ID will also be passed.
	"""
	requires_blog = True

	def default_args(self, client):
		if self.requires_blog:
			return (client.blog_id, client.username, client.password)
		else:
			return (client.username, client.password)