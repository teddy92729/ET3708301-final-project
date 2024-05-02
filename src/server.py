from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet
from time import time


def server(source: Address, target: Address, timeout: int = 2) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        print(f"Server started at {source}")
        buffer = {}
        while True:
            try:
                data = skt.recv(65535)
                pkt = Packet.decode(data)
                skt.sendto(Packet.encode(pkt), tuple(target))
                if buffer.get(pkt.packet_num) is None:
                    now = time()
                    buffer[pkt.packet_num] = now
                    print(f"Received packet at {now}: {pkt}")
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
