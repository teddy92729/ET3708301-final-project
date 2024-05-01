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

        if i == window:
            window = min(window * 2, len(pkts) - index)
        else:
            window = base_window
        index += i


if __name__ == "__main__":

    proxy(delay=0.5, loss=0.01)
    proxy(receiver=host_port("127.0.0.1", 5406), delay=0.1, loss=0.1)

    pkts = [packet() for _ in range(1000)]
    net1 = network(timeout=2)
    net2 = network(
        sender=host_port("127.0.0.1", 5406),
        receiver=host_port("127.0.0.1", 5407),
        timeout=2,
    )
    net2.rsock.close()
    net2.rsock = net1.rsock
    window_sendto([net1, net2], pkts)
    print("done")
