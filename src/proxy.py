from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet
from threading import Thread
from random import uniform
from time import sleep


def proxy(
    source: Address,
    target: Address,
    delay: tuple[float, float] = (0, 0),
    loss: float = 0,
) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind((source.host, source.port))
        print(f"Proxy server started at {source}")

        def delay_sendto(data: bytes) -> None:
            sleep(delay[1])
            skt.sendto(data, tuple(target))

        while True:
            try:
                data, _ = skt.recvfrom(65535)
                if uniform(0, 1) < loss:
                    print(f"Packet <{data}> lost")
                    continue
                if uniform(0, 1) < delay[1]:
                    print(f"Delaying packet <{data}> for {delay[1]:.5f} seconds")
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
    args = parser.parse_args()

    proxy(args.source, args.target, args.delay, args.loss)
