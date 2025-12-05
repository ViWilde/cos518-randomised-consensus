import random
from server import *
from network import *


class System:
    # The idea is that different systems will reimplement the `run_undistributed` and `spawn_servers` functions in more hostile ways; crashing servers, initialising weird values, etc.
    def __init__(self, n, f, network, cutoff=0, seed=0, *args, **kwargs) -> None:
        assert 5 * f < n  # Threshold for correctness guarantee
        self.step_count = 0
        self.rounds = 0
        self.n = n
        self.f = f
        self.network = network
        self.servers = [Server()] * n
        self.evil_ids = set()
        self.randomness = random.Random(seed)
        self.cutoff = cutoff
        # self.val_generator = val_generator  # generate values for servers; a mapping from [n] -> (space of possible vals)
        # self.scheduler = scheduler  # scheduler - a function from a step count c (and the server count n) to telling you which server you should run on that step. So mapping N x n -> [n]

        # Hacks FIXME
        # self.evil_constructor = evil_constructor  # A constructor for evil servers

        self.spawn_servers()
        # self.print_state()

    def print_state(self):
        print([s.x for s in self.servers])

    def finish(self):
        data = {
            "steps": self.step_count,
            "messages": self.total_messages(),
            "rounds": self.rounds,
        }
        if self.verify_consensus():
            return {"success": True} | data
        elif self.cutoff and self.rounds >= self.cutoff:
            return {"success": False} | data

        else:
            # Should be unreachable
            print("ERROR: Failed, somehow")
            self.print_state()
            return {
                "success": False,
                "steps": self.step_count,
                "rounds": self.rounds,
                "messages": self.total_messages(),
            }

    def run_undistributed(self):
        while self.should_keep_running():
            self.step_count += 1
            next_server = self.step_count % self.n
            self.servers[next_server].primitive_step()
            if next_server == 0:
                self.rounds += 1
        return self.finish()

    def spawn_servers(self):
        self.evil_ids = set(self.randomness.sample(range(self.n), self.f))
        for i in range(self.n):
            # Only spawn honest servers - later implementations will have trickier behaviour
            self.servers[i] = Server(
                self.network, i, self.randomness.randint(0, 1), self.n, self.f
            )
        # values should be random, this is an experiment random.randint(0, 1), HACK

    def get_honest_ids(self):
        return set(range(self.n)) - self.evil_ids

    def get_evil_ids(self):
        return self.evil_ids

    def verify_consensus(self):
        honest = self.get_honest_ids()
        idx = next(
            iter(honest)
        )  # Pick a random element without deleting it. Not great.
        expected = self.servers[idx].x
        for i in honest:
            if self.servers[i].x != expected:
                return False
        self.decided_value = expected
        return True

    def should_keep_running(self):
        return not (self.is_completed() or (self.cutoff and self.rounds >= self.cutoff))

    def is_completed(self):
        for i in self.get_honest_ids():
            if not self.servers[i].done:
                return False
        return True

    def total_rounds(self):
        return max(self.get_honest_ids(), key=lambda i: self.servers[i].final_round)

    def total_messages(self):
        return self.network.message_count

    # def last_round(self):
    #     return self.rounds
    # return max(self.servers, key=lambda s: s.final_round).final_round


class EvilSystem(System):
    def __init__(self, *args, **kwargs) -> None:
        self.evil_class = kwargs.get("evil_class", Server)
        super().__init__(*args, **kwargs)

    def run_undistributed(self):
        while self.should_keep_running():
            self.step_count += 1
            next_server = (
                self.step_count % self.n
            )  # TODO this is the step we want to override
            self.servers[next_server].primitive_step()

            if next_server == 0:
                self.rounds += 1
        return self.finish()

    def spawn_servers(self):
        self.evil_ids = set(self.randomness.sample(range(self.n), self.f))
        for i in range(self.n):
            if i in self.evil_ids:
                self.servers[i] = self.evil_class(
                    self.network, i, self.randomness.randint(0, 1), self.n, self.f
                )

            else:
                self.servers[i] = Server(
                    self.network, i, self.randomness.randint(0, 1), self.n, self.f
                )


class EvilHotswapSystem(EvilSystem):
    # Every time we step a server, we have a `flip_chance` probability to change it from good to evil (or vice versa) , and also of some other server (to maintain balance)
    def __init__(self, *args, **kwargs):
        self.flip_chance = kwargs.get("flip_chance", 0.2)
        super().__init__(*args, **kwargs)

    def find_flippable(self, options):
        # Pick a server from `options` that is not done (if one exists), and hotswap it with new_constructor
        still_running = [i for i in options if not self.servers[i].done]
        if still_running:
            flipped = self.randomness.choice(still_running)
            return flipped  # We should flip this server
        return None

    def swap_servers(self, good_id, evil_id):
        # Turns good_id into an evil server, and evil_id into a good server, preserving state of both

        self.servers[good_id] = self.evil_class.from_server(self.servers[good_id])
        self.evil_ids.add(good_id)

        self.servers[evil_id] = Server.from_server(self.servers[evil_id])
        self.evil_ids.remove(evil_id)

    def run_undistributed(self):
        while self.should_keep_running():
            self.step_count += 1
            next_server = self.step_count % self.n
            self.servers[next_server].primitive_step()
            if next_server == 0:
                # At the start of a new round, the world is filled with possibilities
                self.rounds += 1
                if self.randomness.random() < self.flip_chance:
                    currently_good = self.find_flippable(self.get_honest_ids())
                    currently_evil = self.find_flippable(self.get_evil_ids())
                    if currently_evil and currently_good:  # both exist to be flipped
                        self.swap_servers(currently_good, currently_evil)

        return self.finish()
