from network import *
import random


class proxy:
    def __init__(
        self,
        sender: host_port,
        receiver: host_port,
        timeout: int = 10,
        delay: tuple[float] = (0.1, 0.5),
        loss: float = 0.1,
    ):
        self.sender: host_port = sender
        self.receiver: host_port = receiver
        self.ssock: socket = socket(AF_INET, SOCK_DGRAM)
        self.rsock: socket = socket(AF_INET, SOCK_DGRAM)
        self.rsock.bind((self.receiver.host, self.receiver.port))
        self.rsock.settimeout(timeout)
        self.delay = delay
        self.loss = loss

        def delay_sendto(data: bytes):
            nonlocal self
            if random.randint(0, 100) < self.loss * 100:
                return
            if random.randint(0, 100) < self.delay[0] * 100:
                time.sleep(delay[1])
            self.ssock.sendto(data, (self.sender.host, self.sender.port))

        def proxy_thread():
            while True:
                try:
                    data, _ = self.rsock.recvfrom(65535)
                    threading.Thread(target=delay_sendto, args=(data,)).start()
                except:
                    pass

        self.thread = threading.Thread(target=proxy_thread)
        self.thread.start()


if __name__ == "__main__":
    server = host_port("localhost", 5405)
    client = host_port("localhost", 5406)
    proxy(client, server, loss=0.1)
    pkts = [packet() for _ in range(10)]
    net = network(server, client, timeout=2)
    rpkts = net.sendto(pkts)
    print("sent packets:")
    print(*pkts, sep="\n")
    print("-" * 50)
    print("received packets:")
    print(*rpkts, sep="\n")
    print("done")
