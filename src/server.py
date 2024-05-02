from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet
from time import time


def server(source: Address, target: Address, timeout: int = 2) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        print(f"Server started at {source}")
        recv = set()
        while True:
            try:
                data = skt.recv(65535)
                pkt: Packet = Packet.decode(data)
                if pkt not in recv:
                    now = time()
                    recv.add(pkt)
                    print(f"Received packet {now-pkt.time:.5f}: <{pkt}>")

                skt.sendto(Packet.encode(pkt), tuple(target))
            except TimeoutError:
                pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Server")
    parser.add_argument(
        "--source", type=Address.parse, required=True, help="Source host:port"
    )
    parser.add_argument(
        "--target", type=Address.parse, required=True, help="Target host:port"
    )
    parser.add_argument("--timeout", type=int, default=2, help="Timeout")
    args = parser.parse_args()

    server(args.source, args.target, args.timeout)
