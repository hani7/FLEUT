# hardware/bill_acceptor.py
import serial
import time
import threading
import logging
import requests

logger = logging.getLogger(__name__)

BILL_PORT = "/dev/ttyS7"
BAUDRATE = 9600

DJANGO_API_BASE = "http://127.0.0.1:8000"
CREDIT_ENDPOINT = "/api/bill-acceptor/credit/"

# ⚠️ à remplir après tes tests log_tb74.py
CODE_TO_AMOUNT = {
    0x01: 500,
    0x02: 1000,
    0x03: 2000,
}


def _open_serial():
    return serial.Serial(
        port=BILL_PORT,
        baudrate=BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
    )


def notify_django(order_id: int, amount: int):
    url = DJANGO_API_BASE + CREDIT_ENDPOINT
    payload = {"order_id": order_id, "amount": amount}
    try:
        resp = requests.post(url, json=payload, timeout=2)
        resp.raise_for_status()
        logger.info("Crédit %s envoyé pour order %s", amount, order_id)
    except Exception as e:
        logger.error("Erreur notify_django: %s", e)


def parse_frame(data: bytes) -> int | None:
    if not data:
        return None
    code = data[0]
    amount = CODE_TO_AMOUNT.get(code)
    if amount is None:
        logger.warning("Code inconnu TB74: %r", data)
    return amount


def read_loop(order_id: int):
    ser = _open_serial()
    logger.info("Lecture TB74 pour order %s", order_id)
    try:
        while True:
            data = ser.read(16)
            if not data:
                time.sleep(0.05)
                continue
            logger.debug("Trame TB74: %r", data)
            amount = parse_frame(data)
            if amount:
                notify_django(order_id, amount)
    finally:
        ser.close()


def start_reader_thread(order_id: int):
    t = threading.Thread(target=read_loop, args=(order_id,), daemon=True)
    t.start()
    return t
