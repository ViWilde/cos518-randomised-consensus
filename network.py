import random


class Network:
    # A very basic network class - the idea is that hostile networks implement the same interface but have more complex operations
    def __init__(self, num_servers, seed=0):
        self.num_servers = num_servers
        self.queues = [[] for _ in range(num_servers)]
        self.message_count = 0
        self.randomness = random.Random(seed)

    def send(self, dst, payload):
        self.message_count += 1
        self.queues[dst].append(payload)

    def send_to_all(self, payload):
        for q in range(self.num_servers):
            self.send(q, payload)

    def poll(self, dst):
        # Return+Remove a single message (from the front of the queue) addressed to dst
        if self.queues[dst]:
            return self.queues[dst].pop(0)
        else:
            return None  # indicates no content


class SlowNetwork(Network):
    def __init__(self, num_servers, seed, *args, **kwargs):
        self.delay_chance = kwargs.get('delay_chance',0.5)  #  TODO should really be a parameter, not magic number
        super().__init__(num_servers, seed)

    def poll(self, dst):
        if self.randomness.random() < self.delay_chance:
            # message delayed
            return None
        else:
            return super().poll(dst)


class ShuffleNetwork(SlowNetwork):
    def send(self, dst, payload):
        super().send(dst, payload)
        self.randomness.shuffle(self.queues[dst])


class InsertNetwork(SlowNetwork):
    def send(self, dst, payload):
        self.message_count += 1
        s = self.queues[dst]
        if len(s):
            s.insert(self.randomness.randint(0, len(s) - 1), payload)
        else:
            s.append(payload)
