from socket import socket, AF_INET, SOCK_DGRAM
from utils import Address, Packet, Timer
from time import time


def client(source: Address, target: Address, pkts_nums: int, timeout: int = 2) -> None:
    pkts = [Packet() for _ in range(pkts_nums)]
    with socket(AF_INET, SOCK_DGRAM) as skt:
        skt.bind(tuple(source))
        skt.settimeout(timeout)
        print(f"Client started at {source}")

        # window size and threshold for congestion control
        base_window = 4
        window = base_window
        threshold = 16

        total_sent = 0

        timer = Timer()
        # index of first packet in this batch
        index = 0
        while index < len(pkts):
            # prevent out of bounds
            bound_window = min(window, len(pkts) - index)
            # get packets that will be sent
            ready_pkts = pkts[index : index + bound_window]
            print("*" * 50)
            for pkt in ready_pkts:
                total_sent += 1
                skt.sendto(Packet.encode(pkt), tuple(target))
                print(f"Sent packet: <{pkt}>")

            last_ack = None
            pkt = None
            try:
                while True:
                    data = skt.recv(65535)
                    last_ack = pkt
                    pkt: Packet = Packet.decode(data)
                    # if last_ack and pkt != last_ack:
                    #     print(f"Received rtt {time()-pkt.time:.5f}: <{pkt}>")

                    # ack packet is equal to last packet in ready_pkts
                    # all packets are received
                    if pkt.packet_num == ready_pkts[-1].packet_num:
                        index += bound_window
                        if window < threshold:
                            window *= 2
                        else:
                            window += 1
                        break
                    elif last_ack and pkt.packet_num == last_ack.packet_num:
                        total_sent += 1
                        skt.sendto(
                            Packet.encode(
                                ready_pkts[
                                    max(
                                        pkt.packet_num - ready_pkts[0].packet_num + 1, 0
                                    )
                                ]
                            ),
                            tuple(target),
                        )
            except TimeoutError:
                if pkt:  # check last ack packet
                    index += max(pkt.packet_num - ready_pkts[0].packet_num + 1, 0)
                window = base_window
                print("restored window")
        t = timer()
        print(f"Total time: {t:.5f} sec")
        print(f"rtt: {t/pkts_nums:.5f} sec")
        print(
            f"Packets resent rate: {(total_sent - pkts_nums) / pkts_nums * 100:.5f} %"
        )


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
    args = parser.parse_args()

    client(args.source, args.target, args.pkts_num, args.timeout)
