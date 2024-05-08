from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet
from time import time


def server(source: Address, target: Address, timeout: int = 2) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        print(f"Server started at {source}")
        # recived packets buffer
        recv: dict[int, Packet] = dict()
        # max contiguos packet number
        cont = 0
        while True:
            try:
                data = skt.recv(65535)
                pkt: Packet = Packet.decode(data)
                recv[pkt.packet_num] = data
                # find max contiguos packet number
                while (cont + 1) in recv:
                    cont += 1
                    print(f"Received packet <{Packet.decode(recv[cont])}>")
                # send ack to client
                skt.sendto(recv[cont], tuple(target))
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
