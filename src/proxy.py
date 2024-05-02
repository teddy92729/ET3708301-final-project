from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet
from threading import Thread
from random import uniform


def proxy(
    source: Address,
    target: Address,
    delay: tuple[float, float] = (0, 0),
    loss: float = 0,
) -> None:
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind((source.host, source.port))
        print(f"Proxy server started at {source}")
        while True:
            try:
                data, _ = skt.recvfrom(65535)
                pkt = Packet.decode(data)
                print(f"Decoded packet: {pkt}")
                if uniform(0, 1) < loss:
                    print(f"Packet {pkt} lost")
                    continue
                if uniform(0, 1) < delay[1]:
                    delay_time = uniform(*delay)
                    print(f"Delaying packet {pkt} for {delay_time:.5f} seconds")
                    Thread(
                        target=lambda: skt.sendto(data, tuple(target)),
                        args=(),
                        daemon=True,
                    ).start()
                    continue
                skt.sendto(data, tuple(target))
                print(f"Sent packet to {target}")
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
    source = Address(args.source_host, args.source_port)
    target = Address(args.target_host, args.target_port)
    proxy(source, target, args.delay, args.loss)
