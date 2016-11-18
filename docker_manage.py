import docker.client import Client
from docker.errors import APIError

kwargs = kwargs_from_env()

kwargs['tls'].assert_hostname = False

kwargs['tls'].verify = False # Workaround https://github.com/docker/docker-py/issues/465

# Set up the client
client = Client(**kwargs)

HOST_CONFIG = ["binds", "port_bindings", "lxc_conf", "publish_all_ports", "links", "privileged", "dns", "dns_search", "volumes_from", "network_mode", "restart_policy", "cap_add", "cap_drop", "devices", "extra_hosts", "read_only", "pid_mode", "ipc_mode", "security_opt", "ulimits"]

class Client:

	def __init__(self, image, stderr=True, stdout=True, **kwargs):
		
		self.image = image
	
		self.stderr = stderr
		
		self.stdout = stdout 
		
		Host_config = dict((k,v) for k, v in kwargs.items if k in HOST_CONFIG)
		
		kwargs['host_config'] = client.create_host_config(**HOST_CONFIG)
		
		self.host_config = kwargs['host_config'] 
	
		
	def run_container(self, **kwargs):
	
		try:

		 	self.container_id = client.create_container(
				image=self.image,
				host_config=self.host_config,
				**kwargs
			)['Id']

		except APIError as e:
	
			if e.response.status_code == 404:

				if e.explanation and 'No such image' in str(e.explanation):

				client.pull(image=self.image)
				
			else:
		
				raise

		client.start(self.container_id)
		
		return self
	
	def run_container_command(self, command):

		exec_id = client.exec_create(
			container=self.container_id,
			cmd=command,
			stdout=self.stdout,			
			stderr=self.stderr
		)['Id']

		client.exec_start(exec_id, stream=True)

	def container_monitoring(self):
		
		exit_status = client.wait(self.container_id)
	
		if exit_status != 0:

			return client.logs(self.container_id, stdout=stdout, stderr=stderr)
if __name__ == '__main__':
	
	container = Client("debian", 'restart_policy':'on-failure', 'network_mode':'bridge', 'port_bindings':'{8080: 80}')

	container.run_container('mem_limit':'4096m', 'stdin_open':'true', 'tty':'true')
	
	container.run_container_command("ls")

	container.container_monitoring()
