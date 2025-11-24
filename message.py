class Message:
    # Necessary assumption: The =sender= field is always filled in honestly.
    def __init__(self, sender, k, val):
        self.sender = sender
        self.k = k
        self.val = val


class Report(Message):
    pass


class Propose(Message):
    pass
