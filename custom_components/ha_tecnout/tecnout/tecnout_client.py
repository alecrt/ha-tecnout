import logging
import socket
import struct
import threading
import time
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from .entities import (
    ControlPanelInfo,
    GeneralStatus,
    ProgramStatus,
    SetProgramStatusEnum,
    ZoneDetailedStatus,
    ZoneSetting,
)

_LOGGER = logging.getLogger(__name__)


class TecnoOutClient:
    """TecnoOutClient is a class that allows interfacing with Tecnoalarm control panels using the Tecno Out protocol."""

    def __init__(self, host, port: int, user_code: int, passphrase: str, legacy=False, watchdog_interval: Optional[float] = None) -> None:
        """
        Initialize the TecnoOutClient.

        :param host: The IP address of the Tecnoalarm control panel.
        :param port: The port number to connect to.
        :param user_code: The user code for authentication.
        :param passphrase: The passphrase for encryption (optional).
        :param legacy: Boolean flag for legacy hardware compatibility.
        :param watchdog_interval: Interval for watchdog in seconds (optional).
        """
        self.host = host
        self.port = port
        self.legacy = legacy
        # Watchdog settings to prevent broken pipe errors (in seconds)
        self._watchdog_interval: Optional[float] = watchdog_interval
        self._watchdog_stop_event = threading.Event()
        self._watchdog_thread = None
        self._passphrase = (
            self._format_passphrase(passphrase.strip())
            if passphrase
            else self._format_passphrase("")
        )
        self._bcd_user_code = self._get_bcd_user_code(user_code)
        self._sock = None
        self._aes_cipher = None
        self._aes_cipher_response = None
        self._lock = threading.Lock()

    def _format_passphrase(self, passphrase):
        """
        Format the passphrase to be exactly 16 bytes long.

        :param passphrase: The passphrase to format.
        :return: The formatted passphrase.
        """
        if len(passphrase) > 16:
            return passphrase[:16]
        if len(passphrase) < 16:
            return passphrase.ljust(16, "\0")
        return passphrase

    def _init_encryption(self):
        """Initialize the AES encryption for communication."""
        if self._sock is None:
            raise ConnectionError("Socket is not connected")

        iv = get_random_bytes(16)
        self._sock.sendall(iv)
        self._aes_cipher = AES.new(
            self._passphrase.encode("utf-8"), AES.MODE_CFB, iv=iv, segment_size=128
        )
        self._aes_cipher_response = AES.new(
            self._passphrase.encode("utf-8"), AES.MODE_CFB, iv=iv, segment_size=128
        )

    def _receive_response(self):
        """
        Receive a response from the Tecnoalarm control panel.

        :return: The decrypted response data.
        :raises ConnectionError: If not connected.
        :raises ValueError: If the response is invalid.
        """
        if not self._sock:
            raise ConnectionError("You must connect first before receiving responses.")
        if not self._aes_cipher_response:
            raise ConnectionError("AES encryption not initialized.")

        result = self._sock.recv(1024)
        if len(result) == 0:
            raise ConnectionError("Connection closed by remote host")
        result = self._aes_cipher_response.decrypt(result)
        self._verify_crc16(result)
        _LOGGER.debug(
            "Received response: %s", " ".join(f"{byte:02X}" for byte in result)
        )

        if len(result) < 5:
            raise ValueError("Response is too short to contain a valid status byte.")

        status_byte = result[4]
        if status_byte == 0x06:
            return result[6:-2]
        elif status_byte == 0x15:
            raise ValueError("Request was not valid. Received status byte: NAK")
        elif status_byte == 0x0F:
            raise ValueError(
                "Request valid but control panel busy. Received status byte: USY"
            )
        else:
            raise ValueError(f"Unknown response status byte: {status_byte:#02x}")

    def _calculate_crc16(self, msg: bytes) -> bytes:
        """
        Calculate CRC16 using the Modbus RTU polynomial (0xA001) and return it as 2 bytes in little-endian order.

        :param msg: Input message as bytes.
        :return: CRC16 value as 2 bytes in little-endian order.
        """
        crc = 0xFFFF
        for byte in msg:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, byteorder="little")

    def _verify_crc16(self, message: bytes):
        """
        Verify the CRC16 of a received message.

        :param message: The received message including the CRC (last 2 bytes).
        :raises ValueError: If the message is too short or the CRC check fails.
        """
        if len(message) < 2:
            raise ValueError("Message is too short to contain data and CRC.")

        data_to_check = message[:-3] if self.legacy else message[:-2]
        received_crc = message[-2:]

        calculated_crc = self._calculate_crc16(data_to_check)

        if calculated_crc != received_crc:
            raise ValueError("CRC check failed.")

    def _get_bcd_user_code(self, number):
        """
        Convert a given number to BCD format (3 bytes) in little-endian,
        with digits in each byte inverted. Pads with zeros to the end if the code is shorter than 6 digits.

        :param number: The user code number.
        :return: The BCD formatted user code.
        :raises ValueError: If the user code is not between 0 and 999999.

        """
        if not (0 <= number <= 999999):
            raise ValueError("User code must be between 0 and 999999.")

        bcd_str = str(number)
        bcd_str = bcd_str.ljust(6, "0")

        bcd_bytes = [
            (int(bcd_str[i + 1]) << 4) | int(bcd_str[i])
            for i in range(0, len(bcd_str), 2)
        ]

        return bytes(bcd_bytes)

    def connect(self):
        """Establish a TCP connection to the Tecnoalarm control panel and initiate encryption."""
        with self._lock:
            self._sock = socket.create_connection((self.host, self.port), timeout=0.5)
            self._sock.settimeout(None)
            self._init_encryption()
            
            # Start watchdog thread if interval is configured and thread doesn't exist
            if (self._watchdog_interval is not None and 
                (self._watchdog_thread is None or not self._watchdog_thread.is_alive())):
                # Make sure any old thread is cleaned up
                if self._watchdog_thread:
                    self._watchdog_thread = None
                # Reset the stop event before starting new thread
                self._watchdog_stop_event.clear()
                self._watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
                self._watchdog_thread.start()

    def _watchdog_loop(self):
        """Background loop sending periodic keep-alive commands to avoid broken pipes."""
        while not self._watchdog_stop_event.is_set():
            interval = self._watchdog_interval
            if interval is None:
                break
            
            # Use the event to allow interruption during sleep
            if self._watchdog_stop_event.wait(interval):
                break
                
            try:
                # Check if we're still connected before sending command
                if self._sock is None:
                    _LOGGER.warning("Watchdog: Socket is None, skipping keep-alive")
                    continue
                    
                # send lightweight keep-alive (general status)
                self.send_command(0x01)
            except Exception as e:
                _LOGGER.warning("Watchdog detected error '%s', attempting reconnect", e)
                try:
                    self._internal_reconnect()
                except Exception as ex:
                    _LOGGER.error("Watchdog failed to reconnect: %s", ex)
                    # On critical failure, stop the watchdog
                    break

    def _internal_reconnect(self):
        """Internal reconnection method used by watchdog to avoid deadlocks."""
        # Close socket and reset connection state without stopping watchdog
        with self._lock:
            if self._sock:
                try:
                    self._sock.close()
                except:
                    pass  # Ignore errors when closing broken socket
                self._sock = None
                self._aes_cipher = None
                self._aes_cipher_response = None
            
            # Recreate connection
            self._sock = socket.create_connection((self.host, self.port), timeout=0.5)
            self._sock.settimeout(None)
            self._init_encryption()

    def send_command(self, command: int, data: bytes = b""):
        """
        Send a command to the Tecnoalarm control panel.

        :param command: The command byte.
        :param data: Optional data to send with the command.
        :return: The response from the control panel.
        :raises ConnectionError: If not connected.
        """
        with self._lock:
            if not self._sock:
                raise ConnectionError("You must connect first before sending commands.")
            if not self._aes_cipher:
                raise ConnectionError("AES encryption not initialized.")

            stx = 0x02
            length = len(data)
            message = (
                struct.pack("B", stx)
                + self._bcd_user_code
                + struct.pack("B", command)
                + struct.pack("B", length)
                + data
            )
            message += self._calculate_crc16(message[:-1] if self.legacy else message)
            _LOGGER.debug("Sent message: %s", " ".join(f"{byte:02X}" for byte in message))
            message = self._aes_cipher.encrypt(message)
            self._sock.sendall(message)
            return self._receive_response()

    def get_info(self) -> ControlPanelInfo:
        """
        Get the control panel information.

        :return: The control panel information.
        """
        command = 0x28
        response = self.send_command(command)
        return ControlPanelInfo.from_bytes(response)

    def get_general_status(self) -> GeneralStatus:
        """
        Get the general status of the control panel.

        :return: The general status.
        """
        command = 0x01
        response = self.send_command(command)
        return GeneralStatus.from_bytes(response)

    def get_zones_detail(
        self, zones_count: int, zone_from=1
    ) -> list[ZoneDetailedStatus]:
        """
        Get detailed status of multiple zones.

        :param zones_count: The number of zones to retrieve.
        :param zone_from: The starting zone number.
        :return: A list of detailed zone statuses.
        """
        chunk = 32
        all_zones = []
        command_code = 0x0F
        while zones_count > 0:
            chunk_size = min(zones_count, chunk)
            zone_to = zone_from + chunk_size - 1
            response = self.send_command(
                command_code, struct.pack("HH", zone_from, zone_to)
            )
            all_zones.extend(_ZoneDetailedStatusResponse(response, zone_from).zones)
            zones_count -= chunk_size
            zone_from = zone_to + 1
        return all_zones

    def get_zones_description(self, zones_count: int, zone_from=1) -> list[str]:
        """
        Get descriptions of multiple zones.

        :param zones_count: The number of zones to retrieve.
        :param zone_from: The starting zone number.
        :return: A list of zone descriptions.
        """
        all_zones = []
        command_code = 0x21
        while zones_count > 0:
            chunk_size = min(zones_count, 8)
            zone_to = zone_from + chunk_size - 1
            response = self.send_command(
                command_code, struct.pack("HH", zone_from, zone_to)
            )
            all_zones.extend(_GenericDescriptionResponse(response).result)
            zones_count -= chunk_size
            zone_from = zone_to + 1
        return all_zones

    def get_zones_setting(self, zones_count: int, zone_from=1):
        """
        Get settings of multiple zones.

        :param zones_count: The number of zones to retrieve.
        :param zone_from: The starting zone number.
        :return: A list of zone settings.
        """
        all_zones = []
        command_code = 0x20
        while zones_count > 0:
            chunk_size = min(zones_count, 8)
            zone_to = zone_from + chunk_size - 1
            response = self.send_command(
                command_code, struct.pack("HH", zone_from, zone_to)
            )
            for i in range(0, len(response), 8):
                zone_data = response[i : i + 8]
                all_zones.append(ZoneSetting.from_bytes(zone_data))
            zones_count -= chunk_size
            zone_from = zone_to + 1
        return all_zones

    def get_programs_status(self, prg_count: int, prg_from=1) -> list[ProgramStatus]:
        """
        Get the status of multiple programs.

        :param prg_count: The number of programs to retrieve.
        :param prg_from: The starting program number.
        :return: A list of program statuses.
        """
        command = 0x03
        response = self.send_command(command, struct.pack("HH", prg_from, prg_count))
        programs = []
        for idx, byte in enumerate(response):
            programs.append(ProgramStatus.from_bytes(byte, idx + prg_from))
        return programs

    def get_programs_description(self, prg_count: int, prg_from=1) -> list[str]:
        """
        Get descriptions of multiple programs.

        :param prg_count: The number of programs to retrieve.
        :param prg_from: The starting program number.
        :return: A list of program descriptions.
        """
        command_code = 0x22
        all_prgs = []
        while prg_count > 0:
            chunk_size = min(prg_count, 8)
            zone_to = prg_from + chunk_size - 1
            response = self.send_command(
                command_code, struct.pack("HH", prg_from, zone_to)
            )
            all_prgs.extend(_GenericDescriptionResponse(response).result)
            prg_count -= chunk_size
            prg_from = zone_to + 1
        return all_prgs

    def set_program(self, prg_idx: int, prg_status: SetProgramStatusEnum):
        """
        Set the status of a program.

        :param prg_id: The program ID.
        :param prg_status: The status to set.
        :return: The response from the control panel.
        """
        command = 0x10
        return self.send_command(command, struct.pack("HB", prg_idx, prg_status.value))
    
    def set_zone_isolation(self, zone_number: int, isolate: bool):
        """
        Set the isolation status of a zone.

        :param zone_number: The zone number to modify.
        :param isolate: True to isolate the zone, False to reintegrate it.
        :return: The response from the control panel.
        """
        command = 0x11
        operation = 1 if isolate else 0  # 1 = isolate, 0 = reintegrate
        return self.send_command(command, struct.pack("HB", zone_number, operation))

    def get_log(self, log_number: int):
        """
        Get a specific log entry.

        :param log_number: The log entry number.
        :return: The log entry as a string.
        """
        command = 0x06
        self.send_command(command)
        command = 0x07
        response = self.send_command(command, struct.pack("H", log_number))
        return response.decode("utf-8")

    def get_latest_logs(self, logs_count: int):
        """
        Get the latest log entries.

        :param logs_count: The number of log entries to retrieve.
        :return: A list of log entries as strings.
        """
        command = 0x06
        self.send_command(command)
        command = 0x07
        responses = []
        for log_number in range(1, logs_count + 1):
            response = self.send_command(command, struct.pack("H", log_number))
            responses.append(response.decode("utf-8"))
        return responses

    def close(self):
        """Close the connection to the control panel."""
        # Stop watchdog - signal it to stop
        self._watchdog_stop_event.set()
        
        # Don't join the watchdog thread if we're being called from within it
        # This prevents the "cannot join current thread" error
        current_thread = threading.current_thread()
        if self._watchdog_thread and self._watchdog_thread != current_thread:
            try:
                self._watchdog_thread.join(timeout=5.0)  # Add timeout to prevent hanging
            except Exception as e:
                _LOGGER.warning(f"Error joining watchdog thread: {e}")
            self._watchdog_thread = None
        elif self._watchdog_thread == current_thread:
            # If called from watchdog thread, just mark it for cleanup
            self._watchdog_thread = None
            
        with self._lock:
            if self._sock:
                try:
                    self._sock.close()
                except:
                    pass  # Ignore errors when closing broken socket
                self._sock = None
                self._aes_cipher = None
                self._aes_cipher_response = None
                
        # Reset watchdog event for potential reconnections
        self._watchdog_stop_event.clear()

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.close()


class _ZoneDetailedStatusResponse:
    """Represents the response to the 0x0F command for multiple zones."""

    def __init__(self, response: bytes, zone_from: int) -> None:
        if len(response) % 2 != 0:
            raise ValueError("Response length must be a multiple of 2 bytes.")
        self.zones: list[ZoneDetailedStatus] = self.parse_response(response, zone_from)

    def parse_response(self, response: bytes, zone_from: int):
        zones = []
        for i in range(0, len(response), 2):
            zone_data = response[i : i + 2]
            zones.append(ZoneDetailedStatus.from_bytes(zone_data, zone_from + i // 2))
        return zones

    def __repr__(self):
        return f"<ZoneDetailedStatusResponse zones={len(self.zones)}>"

    def to_dict(self):
        """Returns a list of dictionaries representing all zones detailed statuses."""
        return [zone.model_dump() for zone in self.zones]


class _GenericDescriptionResponse:
    def __init__(self, response: bytes) -> None:
        self.result = self.parse_response(response)

    @staticmethod
    def _clean_ascii_string(data: bytes) -> str:
        return data.decode("ascii").rstrip("\x00")

    def parse_response(self, response: bytes):
        zones = []
        for i in range(0, len(response), 30):
            zone_data = response[i : i + 30]
            zones.append(self._clean_ascii_string(zone_data))
        return zones
