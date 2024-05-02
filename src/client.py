from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet
from time import time


def client(
    source: Address, target: Address, pkts: list[Packet], timeout: int = 2
) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        print(f"Client started at {source}")

        window = 16
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
                recv = list(recv)
                recv.sort(key=lambda x: x.packet_num)
                increment = 0
                for pkt in recv:
                    if pkt == pkts[index + increment]:
                        increment += 1
                index += increment


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

    client(
        args.source, args.target, [Packet() for _ in range(args.pkts_num)], args.timeout
    )
