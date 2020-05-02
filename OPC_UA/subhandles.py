import logging

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

    def __init__(self, optimizer, logger=logging.getLogger(__name__)):
        SubHandler.__init__(self, logger)
        self.optimizer = optimizer

    def datachange_notification(self, node, val, data):
        """
        Overrides parent class method to update optimizer state
        """
        self._logger.debug("Update {}:\t {}" .format(node, val))
        self.optimizer.update_state(node.nodeid.Identifier, val)
        self.optimizer.print_state()
