class BabyOptimizer:
    def __init__(self):
        self.factory_state = {}

    def update_state(self, node, val):
        self.factory_state[node] = val

    def print_state(self):
        print('==================== Current Factory State ===============================')
        [print(f"{key}: {value}") for key, value in self.factory_state.items()]
        print('==========================================================================\r\n')

    def generate_path(self):
        pass





