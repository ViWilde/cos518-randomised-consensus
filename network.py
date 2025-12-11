import random


class Network:
    # A very basic network class - the idea is that hostile networks implement the same interface but have more complex operations
    def __init__(self, num_servers, randomness):
        self.n = num_servers
        self.queues = [[] for _ in range(num_servers)]
        self.message_count = 0
        self.randomness = randomness

    def send(self, dst, payload):
        self.message_count += 1
        self.queues[dst].append(payload)

    def send_to_all(self, payload):
        for q in range(self.n):
            self.send(q, payload)

    def poll(self, dst):
        # Return+Remove a single message (from the front of the queue) addressed to dst
        if self.queues[dst]:
            return self.queues[dst].pop(0)
        else:
            return None  # indicates no content


class SlowNetwork(Network):
    def __init__(self, num_servers, randomness, *args, **kwargs):
        self.delay_chance = kwargs.get(
            "delay_chance", 0.5
        )  #  TODO should really be a parameter, not magic number
        super().__init__(num_servers, randomness)

    def poll(self, dst):
        if self.randomness.random() < self.delay_chance:
            # message delayed
            return None
        else:
            return super().poll(dst)


class ShuffleNetwork(Network):
    def send(self, dst, payload):
        super().send(dst, payload)
        self.randomness.shuffle(self.queues[dst])


class InsertNetwork(Network):
    def send(self, dst, payload):
        self.message_count += 1
        s = self.queues[dst]
        if len(s):
            s.insert(self.randomness.randint(0, len(s) - 1), payload)
        else:
            s.append(payload)


class RandomPollNetwork(Network):
    def poll(self, dst):
        q = self.queues[dst]
        if len(q):
            return q.pop(self.randomness.randint(0, len(q) - 1))
        else:
            return None  # indicates no content


class ApproximateNetwork(Network):
    # Retrieve a message from near the front of the queue, but not necessarily at it ; one of the first $n$ messages.
    def poll(self, dst):
        q = self.queues[dst]
        if len(q):
            idx = self.randomness.randint(0, min(len(q), self.n))
            return q.pop(-1 * idx)
        else:
            return None  # indicates no content


class StackNetwork(Network):
    # Opposite of a queue - return most recent messages first
    def poll(self, dst):
        if self.queues[dst]:
            return self.queues[dst].pop(-1)
        else:
            return None  # indicates no content
