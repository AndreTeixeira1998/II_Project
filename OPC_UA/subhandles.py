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
        self._logger.debug("Update {}:\t {}" .format(node, val))


    def event_notification(self, event):
        """
        called for every event notification from server
        """
        self._logger.debug("Event :\t {}" .format(event))

    def status_change_notification(self, status):
        """
        called for every status change notification from server
        """
        self._logger.debug("Status Update :\t {}" .format(status))



class OptimizerSubHandler(SubHandler):
    """
    Subscription handler to be used with optimizer for
    sensor and actuator updates.
    """

    def __init__(self, optimizer, cond, logger=logging.getLogger(__name__)):
        SubHandler.__init__(self, logger)
        self.optimizer = optimizer
        self.encoding = {"c1t3": "Ma_1", "c1t4": "Mb_1", "c1t5": "Mc_1",
                         "c3t3": "Ma_2", "c3t4": "Mb_2", "c3t5": "Mc_2",
                         "c5t3": "Ma_3", "c5t4": "Mb_3", "c5t5": "Mc_3"}
        self.cond = cond

    def datachange_notification(self, node, val, data):
        """
        Overrides parent class method to update optimizer state
        #TODO: esta funçao tem q ser rapida por isso convem
                depois trocar procuras por dicionarios hardcoded.
        """
        self._logger.debug("Update {}:\t {}" .format(node, val))
        if val is True:
            #só quero ver qnd ficam true depois pode-se tirar isto
            print(f'Change on {node.nodeid.Identifier}:  {val}')
            pass
        #CRIAR OUTRO SUB HANDLER
        if str(node.nodeid.Identifier) == "|var|CODESYS Control Win V3 x64.Application.tapetes.at1.Init.x" and val is True:
            print("Release the prisioners")
            self.cond.set()

        for machine in self.encoding.keys():
            if machine in str(node.nodeid.Identifier):
                if "op" in str(node.nodeid.Identifier) and val is True:
                    print(f"pop an operation on {self.encoding[machine]}")
                    op = self.optimizer.state.machines[self.encoding[machine]].op_list.popleft()
                    self.optimizer.print_machine_schedule()
                elif "Init" in str(node.nodeid.Identifier) and val is True:
                    next_op = self.optimizer.state.machines[self.encoding[machine]].op_list[0]
                    if next_op.step == 1:
                        print(f"Send piece: {next_op.piece_id}")
                        self.optimizer.dispatch_queue.append(self.optimizer.state.pieces[next_op.piece_id])
                    else:
                        print(f"Machine {self.encoding[machine]} on standby")
                break

        self.optimizer.update_state(node.nodeid.Identifier, val)
        #self.optimizer.print_state()

