from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet, Timer
from time import time
import logging


def client(
    source: Address,
    target: Address,
    pkts_num: int,
    timeout: int = 2,
    fast_retransmit: int = 3,
    window: int = 16,
    **kwargs,
) -> None:
    pkts = [Packet() for _ in range(pkts_num)]
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        logging.info(f"Client started at {source}")

        total_timer = Timer()
        # index of first packet in this batch
        for pkt in pkts:
            skt.sendto(Packet.encode(pkt), tuple(target))
            logging.debug(f"Sent packet: <{pkt}>")

        logging.debug("*" * 50)
        t = total_timer()
        logging.info(f"Total time: {t:.5f} sec")
        logging.info(f"Average RTT: {t/pkts_num*1000:.2f} ms")


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
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("--log", type=str, default="client.log", help="Log file")
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

    client(**vars(args))
