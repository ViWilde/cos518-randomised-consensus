import random
from server import EvilServer, IdiotServer, RandomServer, Server
from network import *


class System:
    def __init__(
        self, n, f, network, val_generator, scheduler, evil_constructor
    ) -> None:
        assert 5 * f < n  # Threshold for correctness guarantee
        self.step_count = 0
        self.n = n
        self.f = f
        self.network = network
        self.servers = [0] * n
        self.val_generator = val_generator  # generate values for servers; a mapping from [n] -> (space of possible vals)
        self.scheduler = scheduler  # scheduler - a function from a step count c (and the server count n) to telling you which server you should run on that step. So mapping N x n -> [n]

        # Hacks FIXME
        self.evil_constructor = evil_constructor  # A constructor for evil servers

        self.spawn_servers()
        self.print_state()

    def print_state(self):
        print([s.x for s in self.servers])

    def run_undistributed(self, cutoff=0):
        while not (self.is_completed() or (cutoff and self.step_count >= cutoff)):
            # print(self.step_count)
            self.step_count += 1
            next_server = self.scheduler(self.step_count, self.n)
            self.servers[next_server].primitive_step()
            # print(self.servers[next_server].state)

        if self.verify_consensus():
            print(
                f"""
Consensus Achieved!
Total steps: {self.step_count}
Total messages passed: {self.total_messages()}
                """
            )
        elif cutoff and self.step_count >= cutoff:
            print(f"Failed: Reached cutoff {cutoff}")
        else:
            self.print_state()

    def spawn_servers(self):
        self.evil_ids = random.sample(range(self.n), self.f)
        for i in range(self.n):
            if i in self.evil_ids:
                # spin up a malicious server TODO
                self.servers[i] = self.evil_constructor(
                    self.network, i, self.val_generator(i), self.n, self.f
                )

                pass
            else:
                self.servers[i] = Server(
                    self.network, i, self.val_generator(i), self.n, self.f
                )

    def honest_servers(self):
        return [s for s in self.servers if s.id not in self.evil_ids]

    def evil_servers(self):
        return [s for s in self.servers if s.id in self.evil_ids]

    def verify_consensus(self):
        honest = self.honest_servers()
        expected = honest[0].x
        for s in honest:
            if s.x != expected:
                return False
        return True

    def is_completed(self):
        for s in self.honest_servers():
            if not s.done:
                return False
        return True

    def total_rounds(self):
        return max(self.honest_servers(), key=lambda s: s.final_round)

    def total_messages(self):
        return self.network.message_count


def test_servers():
    n = 25
    f = 4  # <1/5
    cutoff = 10**4
    val_generator = lambda _: random.randint(0, 1)
    scheduler = lambda c, n: c % n  # Step servers in order, nice and easy

    # Control - all honest
    sys = System(n, f, Network(n), val_generator, scheduler, Server)
    sys.run_undistributed(cutoff)

    sys = System(n, f, Network(n), val_generator, scheduler, EvilServer)
    sys.run_undistributed(cutoff)

    sys = System(n, f, Network(n), val_generator, scheduler, RandomServer)
    sys.run_undistributed(cutoff)

    sys = System(n, f, Network(n), val_generator, scheduler, IdiotServer)
    sys.run_undistributed(cutoff)


def test_network():
    n = 25
    f = 4  # <1/5
    cutoff = 10**4
    val_generator = lambda _: random.randint(0, 1)
    scheduler = lambda c, n: c % n  # Step servers in order, nice and easy

    # Control - all honest
    sys = System(n, f, Network(n), val_generator, scheduler, Server)
    sys.run_undistributed(cutoff)

    sys = System(n, f, SlowNetwork(n), val_generator, scheduler, EvilServer)
    sys.run_undistributed(cutoff)

    # TODO: Messages don't get processed here, so the list to shuffle gets ever-larger, and the system locks up basically.
    sys = System(n, f, ShuffleNetwork(n), val_generator, scheduler, RandomServer)
    sys.run_undistributed(cutoff)


    # TODO: This seems to break termination. Understand why.
    # Hunch: When we see a "wrong phase" message (a Propose when we're looking for Reports, etc.) we should handle them more cleverly, either storing them internally (within the Server instance vars), or somehow not popping them from the network queue (eg: toss them back on at the back somehow, or just have some procedure to peek at messages beyond the front of the queue)
    sys = System(n, f, InsertNetwork(n), val_generator, scheduler, RandomServer)
    sys.run_undistributed(cutoff)





test_servers()
test_network()
