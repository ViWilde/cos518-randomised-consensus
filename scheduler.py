class Scheduler:
    # The scheduler logic
    # Return the next server that should step
    def __init__(self, n, randomness):
        self.n = n
        self.randomness = randomness

    def next_server(self, system):
        return system.step_count%self.n

    def on_new_round(self, system):
        pass

class RandomRoundScheduler(Scheduler):
    def __init__(self, n, randomness):
        super().__init__(n, randomness)
        self.permutation = [i for i in range(n)]

    def next_server(self, system):
        i = system.step_count % self.n
        nxt = self.permutation[i]
        return nxt

    def on_new_round(self,system):
        self.randomness.shuffle(self.permutation)

class RandomScheduler(Scheduler):
    def next_server(self, system):
        # Truly random
        return self.randomness.randint(0, self.n - 1)

class EvilFirstScheduler(Scheduler):
    def __init__(self, n, randomness):
        super().__init__(n, randomness)
        self.permutation = [i for i in range(n)]

    def next_server(self, system):
        i = system.step_count % self.n
        nxt = self.permutation[i]
        return nxt


    def on_new_round(self, system):
        self.permutation = list(system.get_evil_ids()) + list(system.get_honest_ids())
