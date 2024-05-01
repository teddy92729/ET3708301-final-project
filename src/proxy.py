from network import *
import random


class proxy:
    def __init__(
        self,
        sender: host_port = host_port("127.0.0.1", 5404),
        receiver: host_port = host_port("127.0.0.1", 5405),
        timeout: int = 10,
        delay: float = 0.1,
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
            if random.randint(0, 100) < self.delay * 100:
                time.sleep(0.5)
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

    from random import randint

    proxy()
    pkts = [packet() for _ in range(randint(5, 10))]
    net = network(timeout=2)
    rpkts = net.sendto(pkts, delay=0.1)
    print("sent packets:")
    print(*pkts, sep="\n")
    print("-" * 50)
    print("received packets:")
    print(*rpkts, sep="\n")
    print("done")
