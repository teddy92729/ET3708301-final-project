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

        batch = 0
        total_sent = 0
        total_fast_retransmit = 0
        total_timeout = 0

        total_timer = Timer()
        # index of first packet in this batch
        index = 0
        while index < len(pkts):
            batch += 1
            # prevent out of bounds
            bound_window = min(window, len(pkts) - index)
            # get packets that will be sent
            ready_pkts = pkts[index : index + bound_window]
            logging.debug(f"batch {batch}" + "*" * 50)
            for pkt in ready_pkts:
                total_sent += 1
                skt.sendto(Packet.encode(pkt, batch), tuple(target))
                logging.debug(f"Sent packet: <{pkt}>")

            counter = 0
            last_pkt = None
            pkt = None
            offset = -1
            batch_timer = Timer()
            try:
                while True:
                    data = skt.recv(65535)
                    tmp_pkt: Packet = Packet.decode(data)
                    tmp_offset = tmp_pkt - ready_pkts[0]
                    # ignore ack packets that are not in current window
                    if (
                        tmp_offset < -1
                        or tmp_pkt.id != batch
                        or (pkt and (tmp_pkt - pkt) < 0)
                    ):
                        continue
                    last_pkt = pkt
                    pkt = tmp_pkt
                    offset = tmp_offset
                    logging.debug(f"Received ack: <{pkt}>")

                    # ack packet is equal to last packet in ready_pkts
                    # all packets are received
                    if offset == bound_window - 1:
                        index += bound_window
                        logging.debug(
                            f"Window move {bound_window}: all packets received"
                        )
                        break

                    if last_pkt and last_pkt == pkt:
                        counter += 1
                    else:
                        counter = 1

                    # when we receive same ack packets
                    # we can move window to the next packet earlier
                    if fast_retransmit and counter >= fast_retransmit:
                        index += offset + 1
                        total_fast_retransmit += 1
                        logging.debug(f"Window move {offset + 1}: fast retransmit")
                        break
            except TimeoutError:
                index += offset + 1
                total_timeout += 1
                logging.debug(f"Window move {offset + 1}: timeout")
            t = batch_timer()
            logging.debug(f"Time elapsed: {t:.5f} sec")
        t = total_timer()
        logging.info(f"Total time: {t:.5f} sec")
        logging.info(f"Average RTT: {t/pkts_num*1000:.2f} ms")
        logging.info(f"Total packets sent: {total_sent}")
        logging.info(f"Total fast retransmit: {total_fast_retransmit}")
        logging.info(f"Total timeout: {total_timeout}")
        logging.info(
            f"Packets retransmit rate: {(total_sent - pkts_num) / pkts_num * 100:.5f} %"
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
    parser.add_argument(
        "--fast_retransmit",
        type=int,
        default=3,
        help="Fast retransmit (the number of same ack packets; 0 to disable)",
    )
    parser.add_argument("--window", type=int, default=16, help="Window size")
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
