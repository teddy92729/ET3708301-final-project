import time
import re
from socket import socket, AF_INET, SOCK_DGRAM
import threading


class packet:
    pass


class host_port:
    pass


class network:
    pass


class packet:
    packet_num: int = 0

    def __init__(self, packet_data: tuple[int, float] | None = None):
        self.packet_num: int
        self.time: float
        if packet_data is not None:
            self.packet_num = packet_data[0]
            self.time = packet_data[1]
        else:
            packet.packet_num += 1
            self.packet_num = packet.packet_num
            self.time = -1

    def __str__(self) -> str:
        return f"Packet {self.packet_num} sended at t = {self.time:.5f}"

    @staticmethod
    def encode(pkt: packet) -> bytes:
        pkt.time = time.time()
        return str(pkt).encode()

    @staticmethod
    def decode(data: bytes) -> packet | None:
        data = data.decode()
        data = re.search(r"^Packet (\d+) sended at t = (\d+.\d+)$", data).groups()
        try:
            return packet((int(data[0]), float(data[1])))
        except:
            return None


class host_port:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int = port


class network:
    def __init__(
        self,
        sender: host_port = host_port("127.0.0.1", 5405),
        receiver: host_port = host_port("127.0.0.1", 5405),
        timeout: int = 10,
    ):
        self.sender: host_port = sender
        self.receiver: host_port = receiver
        self.ssock: socket = socket(AF_INET, SOCK_DGRAM)
        self.rsock: socket = socket(AF_INET, SOCK_DGRAM)
        self.rsock.bind((self.receiver.host, self.receiver.port))
        self.rsock.settimeout(timeout)

    def sendto(self, pkts: list[packet,]) -> list[int]:
        lock = threading.Lock()
        rpkts: list[packet,] = []

        def recive_packet():
            try:
                data, _ = self.rsock.recvfrom(65535)
                data = packet.decode(data)
                if data is None:
                    return False
                with lock:
                    rpkts.append(data)
            except:
                pass

        def send_packets():
            for pkt in pkts:
                data = packet.encode(pkt)
                self.ssock.sendto(data, (self.sender.host, self.sender.port))

        threads = [threading.Thread(target=recive_packet) for _ in range(len(pkts))] + [
            threading.Thread(target=send_packets)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return [pkt.packet_num for pkt in rpkts]


if __name__ == "__main__":
    import random

    pkts = [packet() for _ in range(random.randint(1, 10))]
    net = network()
    print(net.sendto(pkts))
