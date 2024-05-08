from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet


def client(source: Address, target: Address, pkts_nums: int, timeout: int = 2) -> None:
    pkts = [Packet() for _ in range(pkts_nums)]
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        print(f"Client started at {source}")

        base_window = 4
        window = base_window
        threshold = 16

        index = 0
        # pkts.sort(key=lambda x: x.packet_num)
        while index < len(pkts):
            bound_window = min(window, len(pkts) - index)
            ready_pkts = pkts[index : index + bound_window]
            print("*" * 50)
            for pkt in ready_pkts:
                skt.sendto(Packet.encode(pkt), tuple(target))
                print(f"Sent packet: <{pkt}>")
            recv = set()
            try:
                while True:
                    data = skt.recv(65535)
                    pkt = Packet.decode(data)
                    recv.add(pkt)
            except TimeoutError:
                recv = sorted(recv, key=lambda x: x.packet_num)
                if recv:
                    index += max(recv[-1].packet_num - ready_pkts[0].packet_num + 1, 0)
                    print(f"Received max ack: <{recv[-1]}>")
                if recv and recv[-1] == ready_pkts[-1]:
                    if window < threshold:
                        window *= 2
                    else:
                        window += 1
                else:
                    window = base_window
                    print("restored window")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Client")
    parser.add_argument(
        "--source", type=Address.parse, required=True, help="Source host:port"
    )
    parser.add_argument(
        "--target", type=Address.parse, required=True, help="Target host:port"
    )
    parser.add_argument(
        "--pkts_num", type=int, default=1000, help="Number of packets to send"
    )
    parser.add_argument("--timeout", type=int, default=2, help="Timeout")
    args = parser.parse_args()

    client(args.source, args.target, args.pkts_num, args.timeout)
