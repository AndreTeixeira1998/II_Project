import logging
from Optimizer.transfgraph import Operation


class SubHandler:
	"""
	Generic Subscription Handler. To receive events from server for a subscription
	Do not use heavy methods inside this class
	"""

	def __init__(self, logger=logging.getLogger(__name__)):
		self._logger = logger

	def datachange_notification(self, node, val, data):
		"""
		called for every datachange notification from server
		"""
		self._logger.debug("Update {}:\t {}".format(node, val))

	def event_notification(self, event):
		"""
		called for every event notification from server
		"""
		self._logger.debug("Event :\t {}".format(event))

	def status_change_notification(self, status):
		"""
		called for every status change notification from server
		"""
		self._logger.debug("Status Update :\t {}".format(status))


class OptimizerSubHandler(SubHandler):
	"""
	Subscription handler to be used with optimizer for
	sensor and actuator updates.
	"""

	def __init__(self, optimizer, cond, cond_p1, cond_p2, cond_pusher_1, cond_pusher_2, cond_pusher_3, logger=logging.getLogger(__name__)):
		SubHandler.__init__(self, logger)
		self.optimizer = optimizer
		self.encoding = {"c1t3": "Ma_1", "c1t4": "Mb_1", "c1t5": "Mc_1",
						 "c3t3": "Ma_2", "c3t4": "Mb_2", "c3t5": "Mc_2",
						 "c5t3": "Ma_3", "c5t4": "Mb_3", "c5t5": "Mc_3"}
		self.cond = cond
		self.cond_p1 = cond_p1
		self.cond_p2 = cond_p2
		self.cond_pusher_1 = cond_pusher_1
		self.cond_pusher_2 = cond_pusher_2
		self.cond_pusher_3 = cond_pusher_3

	def datachange_notification(self, node, val, data):
		"""
		Overrides parent class method to update optimizer state
		#TODO: esta funçao tem q ser rapida por isso convem
				depois trocar procuras por dicionarios hardcoded.
		"""

		self.optimizer.factory_state[str(node.nodeid.Identifier)] = val
		# print(self.optimizer.factory_state)

		self._logger.debug("Update {}:\t {}".format(node, val))
		if val is True:
			# só quero ver qnd ficam true depois pode-se tirar isto
			# print(f'Change on {node.nodeid.Identifier}:  {val}')
			pass
		# CRIAR OUTRO SUB HANDLER
		if str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.tapetes.at1.Init.x" and val is True:
			# print("Release the prisioners")
			self.cond.set()

		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.c7t1b_i.sensor" and val is True:
			print("LOCK AND LOAD1")
			self.cond_p1.set()

		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.c7t7b_i.sensor" and val is True:
			print("LOCK AND LOAD2")
			self.cond_p2.set()

		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.vazio_ramp1" and val is True:
			print('UNLOAD SERVICES 1 !!!!')
			self.optimizer.pusher.count_1 = 0
			self.cond_pusher_1.set()

		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.vazio_ramp2" and val is True:
			print('UNLOAD SERVICES 2 !!!!')
			self.optimizer.pusher.count_2 = 0
			self.cond_pusher_2.set()

		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.vazio_ramp3" and val is True:
			print('UNLOAD SERVICES 3 !!!!')
			self.optimizer.pusher.count_3 = 0
			self.cond_pusher_3.set()


		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.piece_array[2].id" and val != 0:
			print(f"Piece {val} complete")
			self.optimizer.tracker.mark_complete(int(val))
			self.optimizer.tracker.print_tracking_info()
			self.optimizer.tracker.print_order_status()
            
		##UNLOAD 1 
		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.la_vai1" and val != 0:
			print(f"Piece {val} unload complete")
			self.optimizer.tracker.mark_unloaded(int(val))
			self.optimizer.tracker.print_tracking_info()
			self.optimizer.tracker.print_order_status()
		##UNLOAD 2 
		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.la_vai2" and val != 0:
			print(f"Piece {val} unload complete")
			self.optimizer.tracker.mark_unloaded(int(val))
			self.optimizer.tracker.print_tracking_info()
			self.optimizer.tracker.print_order_status()            
		##UNLOAD 3 
		elif str(
				node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.GVL.la_vai3" and val != 0:
			print(f"Piece {val} unload complete")
			self.optimizer.tracker.mark_unloaded(int(val))
			self.optimizer.tracker.print_tracking_info()
			self.optimizer.tracker.print_order_status()
            
            
		for machine in self.encoding.keys():
			if machine in str(node.nodeid.Identifier):
				if "op" in str(node.nodeid.Identifier) and val is True:
					# print(f"pop an operation on {self.encoding[machine]}")
					op = self.optimizer.state.machines[self.encoding[machine]].op_list.popleft()
					self.optimizer.print_machine_schedule()
					print(node.nodeid)
					self.optimizer.state.machines[self.encoding[machine]].op_list[0].update_next_tool()

				elif "Init" in str(node.nodeid.Identifier) and val is True:
					self.optimizer.state.machines[self.encoding[machine]].make_available()
				break

		self.optimizer.update_state(node.nodeid.Identifier, val)
	# self.optimizer.print_state()
