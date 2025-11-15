# hardware/doors.py
import serial
import time
import logging

logger = logging.getLogger(__name__)

RS485_PORT = "/dev/ttyS5"
BAUDRATE = 9600


def _get_serial():
    return serial.Serial(
        port=RS485_PORT,
        baudrate=BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
    )


def build_open_door_frame(slot_index: int) -> bytes:
    """
    ⚠️ À adapter avec la vraie trame trouvée via strace.
    Exemple fictif : 0xAA, [slot], 0x55
    """
    if not (0 <= slot_index <= 255):
        raise ValueError("slot_index doit être entre 0 et 255")
    return bytes([0xAA, slot_index, 0x55])


def open_door(slot_index: int) -> bytes | None:
    ser = _get_serial()
    try:
        ser.reset_input_buffer()
        frame = build_open_door_frame(slot_index)
        logger.info("Envoi trame ouverture porte %s: %r", slot_index, frame)
        ser.write(frame)
        ser.flush()
        time.sleep(0.1)
        resp = ser.read(64)
        logger.info("Réponse contrôleur: %r", resp)
        return resp
    finally:
        ser.close()
