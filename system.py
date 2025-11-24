import random
from server import Server
from network import Network

class System:
    def __init__(self, n, f, network, val_generator) -> None:
        assert 5 * f < n  # Threshold for correctness guarantee
        self.n = n
        self.f = f
        self.network = network
        self.servers = []
        self.val_generator = val_generator  # generate values for servers; a mapping from [n] -> (space of possible vals)
        self.spawn_servers()
        return

    def run_distributed_system(self):
        # This is the main loop, and the bit where the actual concurrency code goes.
        # TODO
        pass

    def spawn_servers(self):
        self.evil_ids = random.sample(range(self.n), self.f)
        for i in range(self.n):
            if i in self.evil_ids:
                # spin up a malicious server TODO
                pass
            else:
                self.servers[i] = Server(
                    self.network, i, self.val_generator(i), self.n, self.f
                )

    def honest_servers(self):
        return [s for s in self.servers if s.id not in self.evil_ids]

    def evil_servers(self):
        return [s for s in self.servers if s.id in self.evil_ids]

    def is_completed(self):
        for s in self.honest_servers():
            if not s.done:
                return False
        return True

    def total_rounds(self):
        return max(self.honest_servers(), key=lambda s: s.final_round)

    def total_messages(self):
        return self.network.message_count
