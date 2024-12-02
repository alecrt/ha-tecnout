"""Convinient entities for TecnoOUT client."""

import json
from enum import Enum


class ControlPanelInfo:
    PANEL_TYPE_MAP = {35: "TP20-440", 45: "TP8-88 PLUS", 49: "EV 10-50"}

    def __init__(self, data: bytes) -> None:
        if len(data) != 32:
            raise ValueError("Data must be exactly 32 bytes long.")

        self.firmware_nationality = data[0]
        self.firmware_version = data[1]
        self.hardware_version = data[2]
        self.vocabulary_nationality = data[3]
        self.vocabulary_version = data[4]
        self.panel_type = self.PANEL_TYPE_MAP.get(data[5], "Unknown")
        self.max_zones = int.from_bytes(data[6:8], "little")
        self.associated_zones = int.from_bytes(data[8:10], "little")
        self.codes_count = int.from_bytes(data[10:12], "little")
        self.keys_rfid_count = int.from_bytes(data[12:14], "little")
        self.log_events_count = int.from_bytes(data[14:16], "little")
        self.programs_count = data[16]
        self.remote_controls_count = data[17]
        self.remote_outputs_count = data[18]
        self.scheduled_programmers_count = data[19]
        self.bus_input_modules_count = data[20]
        self.bus_output_expansions_count = data[21]
        self.bus_keypads_count = data[22]
        self.bus_sirens_count = data[23]
        self.bus_key_points_count = data[24]
        self.radio_modules_count = data[25]
        self.radio_keypads_count = data[26]
        self.radio_sirens_count = data[27]
        self.bus_communicators_count = data[28]
        self.crc16 = int.from_bytes(data[30:32], "little")

    def __repr__(self) -> str:
        """Convert the object's properties into a string."""
        return (
            f"<ControlPanelStatus firmware_nationality={self.firmware_nationality}, "
            f"firmware_version={self.firmware_version}, "
            f"hardware_version={self.hardware_version}, ...>"
        )

    def to_dict(self) -> dict:
        """Convert the object's properties into a dictionary for easier inspection."""
        return dict(vars(self).items())


class ZoneDetailedStatus:
    """
    Represents the detailed status of a single zone.

    As described in the 0x0F command response.
    """

    def __init__(self, zone_data: bytes, idx: int) -> None:
        if len(zone_data) != 2:
            raise ValueError("Zone data must be exactly 2 bytes.")
        self.idx = idx
        self._parse_zone_data(zone_data)

    @property
    def description(self) -> None | str:  # noqa: D102
        return self._name

    @description.setter
    def description(self, value: str) -> None:
        self._name = value

    def _parse_zone_data(self, zone_data: bytes) -> None:
        # BYTE 1: First byte of the zone status
        self.isolation_active = bool(zone_data[0] & 0b00000001)
        self.zone_status = bool(zone_data[0] & 0b00000010)
        self.zone_tamper_status = bool(zone_data[0] & 0b00000100)
        self.zone_tamper_alarm = bool(zone_data[0] & 0b00001000)
        self.battery_low = bool(zone_data[0] & 0b00010000)
        self.supervision_alarm = bool(zone_data[0] & 0b00100000)
        self.active_zone = bool(zone_data[0] & 0b01000000)
        self.learned_zone = bool(zone_data[0] & 0b10000000)

        # BYTE 2: Second byte of the zone status
        self.mask_status = bool(zone_data[1] & 0b00000001)
        self.fail_status = bool(zone_data[1] & 0b00000010)
        self.alim_failure = bool(zone_data[1] & 0b00000100)
        self.input_10s_status = bool(zone_data[1] & 0b00001000)
        self.pre_alarm = bool(zone_data[1] & 0b00010000)
        self.alarm = bool(zone_data[1] & 0b00100000)
        self.alarm_24h = bool(zone_data[1] & 0b01000000)
        self.enabled = bool(zone_data[1] & 0b10000000)

    def __repr__(self) -> str:
        """Convert the object's properties into a string."""
        return (
            f"<ZoneDetailedStatus idx={self.idx} enabled={self.enabled} isolation_active={self.isolation_active}, "
            f"zone_tamper_status={self.zone_tamper_status}, zone_tamper_alarm={self.zone_tamper_alarm}, "
            f"battery_low={self.battery_low}, supervision_alarm={self.supervision_alarm}, "
            f"active_zone={self.active_zone}, learned_zone={self.learned_zone}, "
            f"mask_status={self.mask_status}, fail_status={self.fail_status}, zone_status={self.zone_status},"
            f"alim_failure={self.alim_failure}, input_10s_status={self.input_10s_status}, "
            f"pre_alarm={self.pre_alarm}, alarm={self.alarm}, alarm_24h={self.alarm_24h}>"
        )

    def to_dict(self) -> dict:
        """Convert the object's properties into a dictionary for easier inspection."""
        return dict(vars(self).items())

    def to_json(self) -> str:
        """Convert the object's properties into a JSON string."""
        return json.dumps(self.to_dict())

    def __hash__(self) -> int:
        """Calculate the hash of all properties of the object."""
        return hash(
            (
                self.battery_low,
                self.fail_status,
                self.enabled,
                self.idx,
                self.zone_status,
                self.alarm,
                self.pre_alarm,
                self.isolation_active,
                self.active_zone,
                self._name,
            )
        )


class ZoneSetting:
    """Represent a single zone's settings."""

    def __init__(self, zone_data: bytes) -> None:
        if len(zone_data) != 8:
            raise ValueError("Zone data must be exactly 8 bytes.")
        self._parse_zone_data(zone_data)

    def _parse_zone_data(self, zone_data: bytes) -> None:
        # BYTE 1-4: Programs associated to the zone
        self.programs = (
            [bool(zone_data[0] & (1 << i)) for i in range(8)]
            + [bool(zone_data[1] & (1 << i)) for i in range(8)]
            + [bool(zone_data[2] & (1 << i)) for i in range(8)]
            + [bool(zone_data[3] & (1 << i)) for i in range(8)]
        )

        # BYTE 5: Zone type
        zone_types = [
            "excluded",
            "direct",
            "delayed with timer 1",
            "delayed with timer 2",
            "technical",
            "internal",
            "hold-up",
            "pulse key",
            "tamper",
            "MASK",
            "reduced range failure",
            "general failure",
        ]
        self.zone_type = (
            zone_types[zone_data[4]] if zone_data[4] < len(zone_types) else "unknown"
        )

        # BYTE 6: Zone functions (bit flags)
        self.common_zone = bool(zone_data[5] & 0b00000001)
        self.coinciding_zone = bool(zone_data[5] & 0b00000010)
        self.can_be_partset = bool(zone_data[5] & 0b00000100)
        self.cannot_be_excluded = bool(zone_data[5] & 0b00001000)
        # Other bits can be added here if their functions are defined
        self.other_flags = zone_data[5] >> 4  # Bits 4-7 (if needed)

        # BYTE 7-8: Reserved/TBD
        self.reserved = int.from_bytes(zone_data[6:8], byteorder="big")

    def to_dict(self) -> dict:
        """Convert the object's properties into a dictionary for easier inspection."""
        return dict(vars(self).items())

    def to_json(self) -> str:
        """Convert the object's properties into a JSON string."""
        return json.dumps(self.to_dict())

    def __repr__(self) -> str:
        """Convert the object's properties into a string."""
        return (
            f"<ZoneSetting zone_type={self.zone_type}, common_zone={self.common_zone}, "
            f"coinciding_zone={self.coinciding_zone}, can_be_partset={self.can_be_partset}, "
            f"cannot_be_excluded={self.cannot_be_excluded}, programs={self.programs}, "
            f"reserved={self.reserved}>"
        )


class GeneralStatus:
    PANEL_TYPE_MAP = {35: "TP20-440", 45: "TP8-88 PLUS", 49: "EV 10-50"}

    def __init__(self, data: bytes) -> None:
        if len(data) != 16:
            raise ValueError("Response data must be exactly 16 bytes.")
        self._parse_response(data)

    def _parse_response(self, response: bytes) -> None:  # noqa: PLR0915
        self.firmware_language = response[0]
        self.firmware_release = self._decode_release(response[1])
        self.hardware_release = self._decode_release(response[2])
        self.vocabulary_language = response[3] if response[3] != 0xFF else None
        self.vocabulary_release = (
            self._decode_release(response[4]) if response[3] != 0xFF else None
        )
        self.control_panel_type = self.PANEL_TYPE_MAP.get(response[5], "Unknown")

        # BYTE 9 (bit flags)
        self.general_standby = bool(response[8] & 0b00000001)
        self.general_alarm_failure = bool(response[8] & 0b00000010)
        self.general_low_battery = bool(response[8] & 0b00000100)
        self.general_power_failure = bool(response[8] & 0b00001000)
        self.general_tamper = bool(response[8] & 0b00010000)
        self.wireless_failure = bool(response[8] & 0b00100000)
        self.hold_up_status = bool(response[8] & 0b01000000)
        self.technical_status = bool(response[8] & 0b10000000)

        # BYTE 10 (bit flags)
        self.chime_status = bool(response[9] & 0b00000001)
        self.pstn_status = bool(response[9] & 0b00000010)
        self.general_pre_alarm = bool(response[9] & 0b00000100)
        self.pgm_logical_output = bool(response[9] & 0b00001000)
        self.access_denied = bool(response[9] & 0b00010000)
        self.program_alarm = bool(response[9] & 0b00100000)
        self.system_status_ok = bool(response[9] & 0b01000000)
        self.gsm_status = bool(response[9] & 0b10000000)

        # BYTE 11 (bit flags)
        self.general_tamper_alarm = bool(response[10] & 0b00000001)
        self.general_failure_alarm = bool(response[10] & 0b00000010)
        self.false_code_alarm = bool(response[10] & 0b00000100)
        self.false_key_alarm = bool(response[10] & 0b00001000)
        self.general_supervision_alarm = bool(response[10] & 0b00010000)
        self.general_masking_alarm = bool(response[10] & 0b00100000)
        self.general_hold_up_alarm = bool(response[10] & 0b01000000)
        self.general_technical_alarm = bool(response[10] & 0b10000000)

        # BYTE 12 (bit flags)
        self.general_memory_alarm = bool(response[11] & 0b00000001)
        self.active_exit_time = bool(response[11] & 0b00000010)
        self.control_panel_maintenance = bool(response[11] & 0b00000100)
        self.outgoing_call = bool(response[11] & 0b00001000)
        self.end_bypass_signaling = bool(response[11] & 0b00010000)
        self.automatic_arming = bool(response[11] & 0b00100000)
        self.general_isolation_status = bool(response[11] & 0b01000000)
        self.masking_status = bool(response[11] & 0b10000000)

        # BYTE 13 (bit flags)
        self.general_tamper_memory = bool(response[12] & 0b00000001)
        self.failure_memory = bool(response[12] & 0b00000010)
        self.false_code_memory = bool(response[12] & 0b00000100)
        self.false_key_memory = bool(response[12] & 0b00001000)
        self.low_battery_memory = bool(response[12] & 0b00100000)
        self.power_failure_memory = bool(response[12] & 0b01000000)
        self.pstn_memory = bool(response[12] & 0b10000000)

        # BYTE 14 (bit flags)
        self.gsm_alarm_memory = bool(response[13] & 0b00000001)
        self.voice_synthesis_board_present = bool(response[13] & 0b00000010)
        self.incoming_call = bool(response[13] & 0b00000100)
        self.internal_siren_status = bool(response[13] & 0b00001000)
        self.external_siren_status = bool(response[13] & 0b00010000)
        self.out1_status = bool(response[13] & 0b00100000)
        self.out2_status = bool(response[13] & 0b01000000)
        self.local_expansion_present = bool(response[13] & 0b10000000)

        # BYTE 15 (bit flags)
        self.panic_alarm = bool(response[14] & 0b00000001)
        self.internal_siren = bool(response[14] & 0b00000010)
        self.external_siren = bool(response[14] & 0b00000100)

    @staticmethod
    def _decode_release(release_byte: int) -> str:
        major = (release_byte >> 4) & 0x0F
        minor = release_byte & 0x0F
        return f"{major}.{minor}"

    def __repr__(self) -> str:
        """Convert the object's properties into a string."""
        return f"<GeneralStatusResponse firmware_release={self.firmware_release}, hardware_release={self.hardware_release}, system_status_ok={self.system_status_ok}>"

    def to_dict(self) -> dict:
        """Convert the object's properties into a dictionary for easier inspection."""
        return dict(vars(self).items())

    def to_json(self) -> str:
        """Convert the object's properties into a JSON string."""
        return json.dumps(self.to_dict())

    def __hash__(self) -> int:
        """Calculate the hash of all properties of the object."""
        return hash(
            (
                self.general_standby,
                self.general_alarm_failure,
                self.general_low_battery,
                self.general_power_failure,
                self.general_tamper,
                self.wireless_failure,
                self.hold_up_status,
                self.program_alarm,
                self.system_status_ok,
            )
        )


class ProgramStatusEnum(int, Enum):
    """Enumeration for the possible states of a program."""

    STANDBY = 0
    ARMING_PHASE_EXCLUSION = 1
    ARMING_PHASE_EXIT = 2
    ARMED = 3
    END_OF_BYPASS = 4
    PROGRAM_PARSET = 5
    END_OF_BYPASS_SIGNALING = 6


class SetProgramStatusEnum(int, Enum):
    """Enumeration for the possible states of a program to be set from outside."""

    STANDBY = 0  # disinserimento programma
    AUTOARM = 1  # inserimento programma con esclusione automatica delle zone aperte
    ARMED = 2  # inserimento programma SENZA esclusione automatica delle zone aperte
    END_OF_BYPASS = 4  # fine parzializzazione programma
    BYPASS = 5  # inizio parzializzazione programma


class ProgramStatus:
    """Represents the status of a single program."""

    def __init__(self, status_byte: int, idx: int) -> None:
        """Initialize ProgramStatus."""
        self.program_status = ProgramStatusEnum(status_byte & 0x0F)
        self.prealarm = bool(status_byte & 0x10)
        self.alarm = bool(status_byte & 0x20)
        self.alarm_memory = bool(status_byte & 0x40)
        self.reserved = bool(status_byte & 0x80)
        self.idx = idx

    @property
    def name(self) -> None | str:  # noqa: D102
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def __repr__(self) -> str:
        """Convert the object's properties into a string for easier inspection."""
        return (
            f"<Program idx={self.idx} program_status={self.program_status}, prealarm={self.prealarm}, "
            f"alarm={self.alarm}, alarm_memory={self.alarm_memory}, reserved={self.reserved}>"
        )

    def to_dict(self) -> dict:
        """Convert the object's properties into a dictionary for easier inspection."""
        return dict(vars(self).items())

    def to_json(self) -> str:
        """Convert the object's properties into a JSON string."""
        return json.dumps(self.to_dict())

    def __hash__(self) -> int:
        """Calculate the hash of all properties of the object."""
        return hash(
            (
                self.program_status,
                self.prealarm,
                self.alarm,
                self.alarm_memory,
                self.reserved,
                self.idx,
                self._name,
            )
        )
