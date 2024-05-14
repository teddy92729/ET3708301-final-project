from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet
from time import time
import logging


def server(source: Address, target: Address, timeout: int = 2) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        logging.info(f"Server started at {source}")
        # recived packets buffer
        recv: dict[int, Packet] = {0: Packet((0, -1, -1))}
        # max contiguos packet number
        cont = 0
        while True:
            try:
                data = skt.recv(65535)
                pkt: Packet = Packet.decode(data)
                recv[pkt.packet_num] = pkt
                # find max contiguos packet number
                while (cont + 1) in recv:
                    cont += 1
                    logging.debug(f"Received packet <{recv[cont]}>")
                # send ack to client
                skt.sendto(Packet.encode(recv[cont], pkt.id), tuple(target))
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
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("--log", type=str, default="server.log", help="Log file")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            filename=args.log,
            filemode="w",
            level=logging.DEBUG,
            format="%(asctime)s - %(message)s",
        )
    else:
        logging.basicConfig(
            filename=args.log,
            filemode="w",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
        )

    server(args.source, args.target, args.timeout)
