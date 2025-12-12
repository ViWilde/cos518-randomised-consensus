from system import *
from server import *
from network import *
from scheduler import *
from json import dumps
import sys
import math


def scientific_notation(i, exp):
    return i * (10**exp)


def json_string(data):
    return dumps(data, indent=2)


def honest():
    print("Everything Honest")
    n = 6
    f = 1
    r = random.Random()
    sys = System(n, f, Network(n, r), Scheduler(n, r), r, cutoff=1000)
    sys.print_state()
    sys.run_undistributed()


def test_server_network_scheduler(
    servers, networks, schedulers, seed, num_servers, repeats=1
):
    flip_chance = 0.5
    n = num_servers
    f = math.ceil(n / 5) - 1
    cutoff_order = 4
    # cutoff = scientific_notation(n, cutoff_order)
    cutoff = scientific_notation(n, cutoff_order)

    def run_test(server, network, scheduler):
        result = dict()
        result["server"] = server.__name__
        result["network"] = network.__name__
        result["scheduler"] = scheduler.__name__
        result["successes"] = 0
        result["failures"] = 0
        result["base_seed"] = seed
        result["dead_messages"] = 0
        result["rounds"] = 0
        for i in range(repeats):
            randomness = random.Random(seed + i)
            sys = EvilHotswapSystem(
            # sys = EvilSystem(
                n,
                f,
                network(n, randomness),
                scheduler(n, randomness),
                randomness,
                cutoff,
                evil_class=server,
                flip_chance=flip_chance,
            )

            # HACK: Set all to 1 and see if consensus is quick
            # for s in sys.servers:
            #     s.val = 1
            #     s.x = 1
            x = sys.run_undistributed()
            # Rounds and dead_messages are averaged across repeats
            result["rounds"] += x["rounds"] / repeats
            result["dead_messages"] += x["dead_messages"] / repeats
            if x["success"]:
                result["successes"] = result["successes"] + 1
            else:
                result["failures"] = result["failures"] + 1
        return result

    results = []
    for server in servers:
        for network in networks:
            for scheduler in schedulers:
                results.append(run_test(server, network, scheduler))
    print(json_string(results))


def multitest(num, servers, networks, schedulers):
    seed = random.randint(1, 10000)
    test_server_network(servers, networks, schedulers, seed, num)


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
    StackNetwork,
]


schedulers = [Scheduler, RandomRoundScheduler, EvilFirstScheduler]

seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(0, 1000)
# test_servers = lambda servers: test_server_network(servers, [Network], seed)
# test_networks = lambda networks: test_server_network([Server], networks, seed)

test_server_network_scheduler(servers, networks, schedulers, seed, 6, repeats=1)


# 6 servers, 6 networks, 3 schedulers
# total: 108 combinations
# times 5 values of n -> 540
# times 5 repeats -> ~2500 datapoints

# for n in [6, 11, 16, 21, 26]:
#     test_server_network_scheduler(servers, networks, schedulers, seed, n, repeats=5)
