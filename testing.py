from system import *
from server import *
from network import *
from json import dumps
import sys


def scientific_notation(i, exp):
    return i * (10**exp)


def json_string(data):
    return dumps(data, indent=4)


n = 26
f = 5 # <1/5
cutoff = scientific_notation(1, 4)


# TODO why do random servers cause it to fail?
# Abstractly, they correspond to a server that occassionally crashes and spews garbage.
# OH. Subtleties in the state transitions? Because random servers
# But do pseudorandoms (which track state correctly, but broadcast garbage) have the same problem?
# Answer: no. But UnreliableServers do, despite keeping track of state correctly.
# It seems to be annoyingly random. Sometimes they take very little time, other times they take >cutoff.
# Question: In the times where they take >cutoff,


servers = [
    Server,
    EvilServer,
    RandomServer,
    SilentServer,
    UnreliableServer,
    SemirandomServer,
]

# networks = [SlowNetwork, ShuffleNetwork, InsertNetwork]
# networks = [Network, SlowNetwork, InsertNetwork]
# networks = [Network, SlowNetwork]
networks = [Network]


def honest():
    print("_HonestServer_")
    sys = System(n, f, Network(n), cutoff)
    sys.print_state()
    sys.run_undistributed()


def test_server_network(servers, networks, seed):
    flip_chance = 0.1

    def run_test(server, network):
        # print(f"_{server.__name__}, {network.__name__}_")
        sys = EvilHotswapSystem(
            n, f, network(n, seed), cutoff, seed, evil_class=server, flip_chance=flip_chance
        )
        # sys = EvilSystem(n, f, Network(n), seed,evil_class=server)
        result = sys.run_undistributed()
        result["server"] = server.__name__
        result["network"] = network.__name__
        result["seed"] = seed
        return result

    results = []
    for server in servers:
        for network in networks:
            results.append(run_test(server, network))
    print(json_string(results))


def multitest(num):
    for i in range(num):
        seed = random.randint(1, 10000)
        test_server_network(servers, networks, seed)


seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(0, 1000)
test_servers = lambda servers: test_server_network(servers, [Network], seed)
test_networks = lambda networks: test_server_network([Server], networks, seed)

# test_server_network(servers, networks, seed)
# test_networks(networks)

multitest(25)
# honest()
