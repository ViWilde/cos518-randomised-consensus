from system import *
from server import *
from network import *
from json import dumps
import sys


def scientific_notation(i, exp):
    return i * (10**exp)


def json_string(data):
    return dumps(data, indent=2)


n = 16
f = 3  # <1/5
cutoff = scientific_notation(2, 5)


# TODO why do random servers cause it to fail?
# Abstractly, they correspond to a server that occassionally crashes and spews garbage.
# OH. Subtleties in the state transitions? Because random servers
# But do pseudorandoms (which track state correctly, but broadcast garbage) have the same problem?
# Answer: no. But UnreliableServers do, despite keeping track of state correctly.
# It seems to be annoyingly random. Sometimes they take very little time, other times they take >cutoff.
# Question: In the times where they take >cutoff,


def honest():
    print("_HonestServer_")
    sys = System(n, f, Network(n), cutoff)
    sys.print_state()
    sys.run_undistributed()


def test_server_network(servers, networks, seed, repeats=1):
    flip_chance = 0.5

    def run_test(server, network):
        result = dict()
        result["server"] = server.__name__
        result["network"] = network.__name__
        result["successes"] = 0
        result["failures"] = 0
        result["base_seed"] = seed
        result["dead_messages"] = 0
        for i in range(repeats):
            sys = EvilHotswapSystem(
                n,
                f,
                network(n, seed + i),
                cutoff,
                seed + i,
                evil_class=server,
                flip_chance=flip_chance,
            )
            x = sys.run_undistributed()
            result["dead_messages"] = x["dead_messages"]
            result["rounds"] = x["rounds"]
            if x["success"]:
                result["successes"] = result["successes"] + 1
            else:
                result["failures"] = result["failures"] + 1
        return result

    results = []
    for server in servers:
        for network in networks:
            results.append(run_test(server, network))
    print(json_string(results))


def multitest(num, servers, networks):
    seed = random.randint(1, 10000)
    test_server_network(servers, networks, seed, num)


servers = [
    Server,
    EvilServer,
    RandomServer,
    SilentServer,
    UnreliableServer,
    SemirandomServer,
]

networks = [
    Network,
    SlowNetwork,
    InsertNetwork,
    RandomPollNetwork,
    ApproximateNetwork,
]

    # StackNetwork, ShuffleNetwork

seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(0, 1000)
test_servers = lambda servers: test_server_network(servers, [Network], seed)
test_networks = lambda networks: test_server_network([Server], networks, seed)

test_server_network(servers, [SlowNetwork, ApproximateNetwork], seed, repeats=5)

# So. There are 6 servers, 4 networks, so 24 combos. If we run 25 tests via multitest, that's 600 tests.
