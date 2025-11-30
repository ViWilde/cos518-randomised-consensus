class Network:
    # A very basic network class - the idea is that hostile networks implement the same interface but have more complex operations
    def __init__(self, num_servers):
        self.num_servers = num_servers
        self.queues = [[] for _ in range(num_servers)]
        self.message_count = 0

    def send(self, dst, payload):
        self.message_count += 1
        self.queues[dst].append(payload)
        pass

    def send_to_all(self, payload):
        for q in range(self.num_servers):
            self.send(q, payload)

    def poll(self, dst):
        # Return+Remove a single message (from the front of the queue) addressed to dst
        if self.queues[dst]:
            return self.queues[dst].pop(0)
        else:
            return None # indicates no content
