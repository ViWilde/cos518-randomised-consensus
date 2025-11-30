import random

from message import *
from enum import Enum


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


class State(Enum):
    INIT = 1
    REPORTS = 2
    POST_REPORTS = 3
    PROPOSALS = 4
    POST_PROPOSALS = 5
    DONE = 6


class Server:
    def __init__(self, network, id, val, n, f):
        self.network = network
        self.id = id
        self.val = val
        self.x = val
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

        # Primitive step edition
        self.state = State.INIT
        self.seen = set()
        self.histogram = dict()

        # Hack FIXME
        self.possible_values = [0, 1]

    def read_message(self, msg_type):
        msg = self.network.poll(self.id)
        if (
            isinstance(msg, msg_type)
            and msg.k == self.k
            and msg.sender not in self.seen
        ):
            self.seen.add(msg.sender)
            update_count(self.histogram, msg.val)
            self.message_log.append(msg)

    def broadcast(self, msg_type, value):
        self.network.send_to_all(msg_type(self.id, self.k, value))

    def primitive_step(self):
        if self.state == State.INIT:
            self.message_log = []
            self.k += 1
            self.broadcast(Report, self.x)
            self.state = State.REPORTS
        elif self.state == State.REPORTS:
            if len(self.seen) < (self.wait_threshold):
                self.read_message(Report)
            else:
                self.state = State.POST_REPORTS
        elif self.state == State.POST_REPORTS:
            agreed = consensus_values(self.histogram, self.strong_agreement_threshold)
            self.histogram = dict()
            self.seen = set()
            # at most one such element
            # in the non-byzantine version, just n/2 rather than n+f/2
            if agreed:
                self.broadcast(Propose, agreed[0])
            else:
                self.broadcast(Propose, UNKNOWN)
            self.state = State.PROPOSALS
        elif self.state == State.PROPOSALS:
            if len(self.seen) < (self.wait_threshold):
                self.read_message(Propose)
            else:
                self.state = State.POST_PROPOSALS
        elif self.state == State.POST_PROPOSALS:
            self.histogram[UNKNOWN] = 0
            # We disregard these when choosing values, they're just there to pad numbers and get us to n-f
            agreed = consensus_values(self.histogram, self.weak_agreement_threshold)

            majority = consensus_values(self.histogram, self.strong_agreement_threshold)
            if not self.done:
                if majority:
                    self.decide(majority[0])
                elif agreed:
                    self.x = agreed[0]
                else:
                    self.x = random.choice(self.possible_values)
                self.state = State.INIT

    def decide(self, v):
        self.done = True
        self.x = v
        self.final_round = self.k
        # We can't quite /halt/ because that complicates things for other servers. So we just set a flag =done=, that can be observed by the system/supervisor/monitoring.


class RandomServer(Server):
    def __init__(self, *args):
        super().__init__(*args)
        self.state = State.REPORTS

    def send_rand(self, msg_type):
        for i in range(self.n):
            self.network.send(i, msg_type(self.id, self.k, random.randint(0, 1)))

    def primitive_step(self):
        # Flood the zone with garbage
        if self.state == State.REPORTS:
            self.send_rand(Report)
            self.state = State.PROPOSALS
        elif self.state == State.PROPOSALS:
            self.send_rand(Propose)
            self.state = State.REPORTS


class IdiotServer(Server):
    def __init__(self, *args):
        super().__init__(*args)
        self.state = State.REPORTS

    def primitive_step(self):
        if self.state == State.REPORTS:
            self.broadcast(Report, UNKNOWN)
            self.state = State.PROPOSALS
        elif self.state == State.PROPOSALS:
            self.broadcast(Propose, UNKNOWN)
            self.state = State.REPORTS


class EvilServer(Server):
    def __init__(self, *args):
        super().__init__(*args)

    # We just need to modify the broadcast function; primitive_step takes care of the rest.
    def broadcast(self, msg_type, value):
        v=UNKNOWN
        if value == 0:
            v = 1
        elif value == 1:
            v = 0
        else:
            v= random.randint(0, 1)  # handles UNKNOWN
        return super().broadcast(msg_type, v)

    def primitive_step(self):
        return super().primitive_step()

