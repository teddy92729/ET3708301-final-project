from network import *
from proxy import proxy


def multi_sendto(nets: list[network], pkts: list[packet]) -> list[packet]:
    lock = threading.Lock()
    rpkts: list[packet] = []

    def net_thread(n: network, p: list[packet]):
        r = n.sendto(p)
        nonlocal lock
        nonlocal rpkts
        with lock:
            rpkts = rpkts + r

    threads: list[threading.Thread] = [
        threading.Thread(
            target=net_thread,
            args=(n, pkts),
        )
        for n in nets
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return rpkts


def window_sendto(nets: list[network], pkts: list[packet]):
    base_window = 2
    window = base_window
    index = 0

    while index < len(pkts):
        print(f"index: {index}, window: {window}")

        sub_pkts = pkts[index : index + window]
        rpkts = multi_sendto(nets, sub_pkts)
        print(*rpkts, sep="\n")

        snums = [pkt.packet_num for pkt in sub_pkts]
        rnums = [pkt.packet_num for pkt in rpkts]
        rnums.sort()

        i, j = 0, 0
        while i < len(snums) and j < len(rnums):
            if snums[i] == rnums[j]:
                i += 1
                j += 1
            elif snums[i] > rnums[j]:
                j += 1
            else:
                break
        index += i
        if i == window:
            window = min(window * 2, len(pkts) - index)
        else:
            window = min(base_window, len(pkts) - index)


if __name__ == "__main__":
    server = host_port("127.0.0.1", 5404)
    client = host_port("127.0.0.1", 5406)
    proxy1 = host_port("127.0.0.1", 5405)
    proxy2 = host_port("127.0.0.1", 10001)

    proxy(server, proxy1, loss=0.1)
    proxy(server, proxy2, loss=0.1)

    pkts = [packet() for _ in range(1000)]
    net1 = network(proxy1, server, timeout=2)
    net2 = network(proxy2, server, timeout=2)

    window_sendto([net1, net2], pkts)
    print("done")
