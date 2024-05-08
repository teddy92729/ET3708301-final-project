from time import time
import re
from typing import TypeVar

_Packet = TypeVar("_Packet", bound="Packet")


class Packet:
    # static variable to get total number of packets
    __packet_num: int = 0

    def __init__(self, packet_data: tuple[int, float] | None = None) -> None:
        if packet_data is None:
            Packet.__packet_num += 1
            self.__packet_num: int = Packet.__packet_num
            self.__time: float = -1
        else:
            self.__packet_num, self.__time = packet_data

    @property
    def packet_num(self) -> int:
        return self.__packet_num

    @property
    def time(self) -> float:
        return self.__time

    @time.setter
    def time(self, value: float) -> None:
        self.__time = value

    def __str__(self) -> str:
        # define string representation of packet
        return f"Packet {self.__packet_num} sended at t = {self.__time:.5f}"

    def __eq__(self, value: _Packet) -> bool:
        # define equality of packets
        return self.__packet_num == value.__packet_num

    def __hash__(self) -> int:
        return self.packet_num

    @staticmethod
    def encode(pkt: _Packet) -> bytes:
        # record time and encode packet to bytes
        pkt.__time = time()
        return str(pkt).encode()

    @staticmethod
    def decode(data: bytes) -> _Packet:
        # decode packet from bytes and try to parse with regex
        # if parsing fails return None
        data = data.decode()
        data = re.search(r"^Packet (\d+) sended at t = (\d+\.\d+)$", data).groups()
        try:
            return Packet((int(data[0]), float(data[1])))
        except:
            raise ValueError("Invalid packet data")


class Address:
    def __init__(self, host: str, port: int):
        self.__host: str = host
        self.__port: int = port
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", self.__host) is None:
            raise ValueError("Invalid host address")
        if self.__port < 0 or self.__port > 65535:
            raise ValueError("Invalid port number")

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    def __str__(self) -> str:
        return f"{self.__host}:{self.__port}"

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> tuple[str, int]:
        return (self.__host, self.__port).__iter__()

    @staticmethod
    def parse(address: str) -> "Address":
        host, port = re.search(
            r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$", address
        ).groups()
        return Address(host, int(port))


class Timer:
    def __init__(self) -> None:
        self.__start_time: float = time()

    def __call__(self) -> float:
        return time() - self.__start_time

    def reset(self) -> None:
        self.__start_time = time()


if __name__ == "__main__":
    pass
