from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address
from threading import Thread
from random import uniform
from time import sleep
import logging


def proxy(
    source: Address,
    target: Address,
    delay: tuple[float, float] = (0, 0),
    loss: float = 0,
) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind((source.host, source.port))
        logging.info(f"Proxy server started at {source}")

        def delay_sendto(data: bytes) -> None:
            sleep(delay[1])
            skt.sendto(data, tuple(target))

        while True:
            try:
                data, _ = skt.recvfrom(65535)
                if uniform(0, 1) < loss:
                    logging.debug(f"Packet <{data}> lost")
                    continue
                if uniform(0, 1) < delay[1]:
                    logging.debug(
                        f"Delaying packet <{data}> for {delay[1]:.5f} seconds"
                    )
                    Thread(
                        target=delay_sendto,
                        args=(data,),
                        daemon=True,
                    ).start()
                    continue
                skt.sendto(data, tuple(target))
            except TimeoutError:
                pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Proxy server")
    parser.add_argument(
        "--source", type=Address.parse, required=True, help="Source host:port"
    )
    parser.add_argument(
        "--target", type=Address.parse, required=True, help="Target host:port"
    )
    parser.add_argument(
        "--delay", type=float, nargs=2, default=[0, 0], help="Delay (range, seconds)"
    )
    parser.add_argument("--loss", type=float, default=0, help="Loss probability")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("--log", type=str, default="proxy.log", help="Log file")
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

    proxy(args.source, args.target, args.delay, args.loss)
