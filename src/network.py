import time
import re
from socket import socket, AF_INET, SOCK_DGRAM
import threading


class packet:
    pass


class packet:
    # static variable to get total number of packets
    packet_num: int = 0

    def __init__(self, packet_data: tuple[int, float] | None = None):
        self.packet_num: int
        self.time: float
        # if packet_data is not None parse it
        if packet_data is not None:
            self.packet_num = packet_data[0]
            self.time = packet_data[1]
        else:
            # if packet_data is None then set new packet_num and reset time
            packet.packet_num += 1
            self.packet_num = packet.packet_num
            self.time = -1

    def __str__(self) -> str:
        # define string representation of packet
        return f"Packet {self.packet_num} sended at t = {self.time:.5f}"

    def __eq__(self, value: packet) -> bool:
        # define equality of packets
        return self.packet_num == value.packet_num and self.time == value.time

    @staticmethod
    def encode(pkt: packet) -> bytes:
        # record time and encode packet to bytes
        pkt.time = time.time()
        return str(pkt).encode()

    @staticmethod
    def decode(data: bytes) -> packet | None:
        # decode packet from bytes and try to parse with regex
        # if parsing fails return None
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
        receiver: host_port = host_port("127.0.0.1", 5404),
        timeout: int = 10,
    ):
        # network has dual socket for sending and receiving packets
        self.sender: host_port = sender
        self.receiver: host_port = receiver
        self.ssock: socket = socket(AF_INET, SOCK_DGRAM)
        self.rsock: socket = socket(AF_INET, SOCK_DGRAM)
        self.rsock.bind((self.receiver.host, self.receiver.port))
        self.rsock.settimeout(timeout)
        self.rlock = threading.Lock()

    def sendto(self, pkts: list[packet,]) -> list[packet,]:
        # received packets
        rpkts: list[packet,] = []

        # function to recive packet
        def recive_packet():
            try:
                for _ in pkts:
                    with self.rlock:
                        data, _ = self.rsock.recvfrom(65535)
                        data = packet.decode(data)
                        if data is not None:
                            rpkts.append(data)
            except:
                pass

        # function to send packets
        def send_packets():
            for pkt in pkts:
                data = packet.encode(pkt)
                self.ssock.sendto(data, (self.sender.host, self.sender.port))

        thread = threading.Thread(target=recive_packet)
        thread.start()
        send_packets()
        thread.join()
        return rpkts


if __name__ == "__main__":

    pkts = [packet() for _ in range(10)]
    net = network(receiver=host_port("127.0.0.1", 5405), timeout=2)
    print("beginning")
    rpkts = net.sendto(pkts)
    print("sent packets:")
    print(*pkts, sep="\n")
    print("-" * 50)
    print("received packets:")
    print(*rpkts, sep="\n")
