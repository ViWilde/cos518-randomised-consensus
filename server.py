import random
# from network import Network
from message import *


class UnknownVal:
    pass


UNKNOWN = UnknownVal()


def update_count(histogram, entry):
    if entry in histogram.keys():
        histogram[entry] += 1
    else:
        histogram[entry] = 0


def consensus_values(histogram, threshold):
    return [val for (val, count) in histogram.items() if count > threshold / 2]


class Server:
    def __init__(self, network, id, val, n, f):
        self.network = network
        self.id = id
        self.val = val
        self.x = self.val
        self.k = 0
        self.final_round = -1  # The round we finished in
        self.n = n
        self.f = f
        self.strong_agreement_threshold = (n + f) / 2
        self.weak_agreement_threshold = f + 1
        self.wait_threshold = n - f

        self.message_log = []
        # For state tracking/history, essentially - track received messages

        self.done = False

    def step(self):
        self.k += 1
        self.network.send_all(Report(self.id, self.k, self.x))

        reports = self.wait_for(Report)
        agreed = consensus_values(reports, self.strong_agreement_threshold)
        # at most one such element
        # in the non-byzantine version, just n/2 rather than n+f/2
        if agreed:
            self.network.send_all(Propose(self.id, self.k, agreed[0]))
        else:
            self.network.send_all((Propose(self.id, self.k, UNKNOWN)))

        proposals = self.wait_for(Propose)
        proposals[UNKNOWN] = 0
        # We disregard these when choosing values, they're just there to pad numbers and get us to n-f
        agreed = consensus_values(proposals, self.weak_agreement_threshold)

        majority = consensus_values(proposals, self.strong_agreement_threshold)

        if majority:
            self.decide(majority[0])
        elif agreed:
            self.x = agreed[0]
        else:
            self.x = random.choice(possible_values)
            # TODO how do we define this set in the general case?

    def wait_for(self, msg_type):
        seen = set()
        histogram = dict()
        while len(seen) < (self.wait_threshold):
            msg = self.network.poll(self.id)
            if isinstance(msg, msg_type) and msg.k == self.k and msg.sender not in seen:
                seen.add(msg.sender)
                update_count(histogram, msg.val)
        return histogram
        # TODO: What if we accidentally eat messages of the wrong type? Can we safely discard them? Probably not. But maybe yes? Game this out.

    def decide(self, v):
        self.done = True
        self.x = v
        self.final_round = self.k
        # We can't quite /halt/ because that complicates things for other servers. So we just set a flag =done=, that can be observed by the system/supervisor/monitoring.




