"""Convenient entities for TecnoOUT client."""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, ClassVar


class ControlPanelInfo(BaseModel):
    firmware_nationality: int
    firmware_version: int
    hardware_version: int
    vocabulary_nationality: int
    vocabulary_version: int
    panel_type: str
    max_zones: int
    associated_zones: int
    codes_count: int
    keys_rfid_count: int
    log_events_count: int
    programs_count: int
    remote_controls_count: int
    remote_outputs_count: int
    scheduled_programmers_count: int
    bus_input_modules_count: int
    bus_output_expansions_count: int
    bus_keypads_count: int
    bus_sirens_count: int
    bus_key_points_count: int
    radio_modules_count: int
    radio_keypads_count: int
    radio_sirens_count: int
    bus_communicators_count: int
    crc16: int

    PANEL_TYPE_MAP: ClassVar[dict[int, str]] = {35: "TP20-440", 45: "TP8-88 PLUS", 49: "EV 10-50"}

    @classmethod
    def from_bytes(cls, data: bytes) -> "ControlPanelInfo":
        if len(data) != 32:
            raise ValueError("Data must be exactly 32 bytes long.")
        return cls(
            firmware_nationality=data[0],
            firmware_version=data[1],
            hardware_version=data[2],
            vocabulary_nationality=data[3],
            vocabulary_version=data[4],
            panel_type=cls.PANEL_TYPE_MAP.get(data[5], "Unknown"),
            max_zones=int.from_bytes(data[6:8], "little"),
            associated_zones=int.from_bytes(data[8:10], "little"),
            codes_count=int.from_bytes(data[10:12], "little"),
            keys_rfid_count=int.from_bytes(data[12:14], "little"),
            log_events_count=int.from_bytes(data[14:16], "little"),
            programs_count=data[16],
            remote_controls_count=data[17],
            remote_outputs_count=data[18],
            scheduled_programmers_count=data[19],
            bus_input_modules_count=data[20],
            bus_output_expansions_count=data[21],
            bus_keypads_count=data[22],
            bus_sirens_count=data[23],
            bus_key_points_count=data[24],
            radio_modules_count=data[25],
            radio_keypads_count=data[26],
            radio_sirens_count=data[27],
            bus_communicators_count=data[28],
            crc16=int.from_bytes(data[30:32], "little"),
        )


class ZoneDetailedStatus(BaseModel):
    idx: int
    isolation_active: bool
    zone_status: bool
    zone_tamper_status: bool
    zone_tamper_alarm: bool
    battery_low: bool
    supervision_alarm: bool
    active_zone: bool
    learned_zone: bool
    mask_status: bool
    fail_status: bool
    alim_failure: bool
    input_10s_status: bool
    pre_alarm: bool
    alarm: bool
    alarm_24h: bool
    enabled: bool
    description: Optional[str] = None

    @classmethod
    def from_bytes(cls, zone_data: bytes, idx: int) -> "ZoneDetailedStatus":
        if len(zone_data) != 2:
            raise ValueError("Zone data must be exactly 2 bytes.")
        return cls(
            idx=idx,
            isolation_active=bool(zone_data[0] & 0b00000001),
            zone_status=bool(zone_data[0] & 0b00000010),
            zone_tamper_status=bool(zone_data[0] & 0b00000100),
            zone_tamper_alarm=bool(zone_data[0] & 0b00001000),
            battery_low=bool(zone_data[0] & 0b00010000),
            supervision_alarm=bool(zone_data[0] & 0b00100000),
            active_zone=bool(zone_data[0] & 0b01000000),
            learned_zone=bool(zone_data[0] & 0b10000000),
            mask_status=bool(zone_data[1] & 0b00000001),
            fail_status=bool(zone_data[1] & 0b00000010),
            alim_failure=bool(zone_data[1] & 0b00000100),
            input_10s_status=bool(zone_data[1] & 0b00001000),
            pre_alarm=bool(zone_data[1] & 0b00010000),
            alarm=bool(zone_data[1] & 0b00100000),
            alarm_24h=bool(zone_data[1] & 0b01000000),
            enabled=bool(zone_data[1] & 0b10000000),
        )

    def __hash__(self) -> int:
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
                self.description,
            )
        )


class ZoneSetting(BaseModel):
    programs: list
    zone_type: str
    common_zone: bool
    coinciding_zone: bool
    can_be_partset: bool
    cannot_be_excluded: bool
    other_flags: int
    reserved: int

    @classmethod
    def from_bytes(cls, zone_data: bytes) -> "ZoneSetting":
        if len(zone_data) != 8:
            raise ValueError("Zone data must be exactly 8 bytes.")
        programs = (
            [bool(zone_data[0] & (1 << i)) for i in range(8)]
            + [bool(zone_data[1] & (1 << i)) for i in range(8)]
            + [bool(zone_data[2] & (1 << i)) for i in range(8)]
            + [bool(zone_data[3] & (1 << i)) for i in range(8)]
        )
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
        zone_type = (
            zone_types[zone_data[4]] if zone_data[4] < len(zone_types) else "unknown"
        )
        return cls(
            programs=programs,
            zone_type=zone_type,
            common_zone=bool(zone_data[5] & 0b00000001),
            coinciding_zone=bool(zone_data[5] & 0b00000010),
            can_be_partset=bool(zone_data[5] & 0b00000100),
            cannot_be_excluded=bool(zone_data[5] & 0b00001000),
            other_flags=zone_data[5] >> 4,
            reserved=int.from_bytes(zone_data[6:8], byteorder="big"),
        )


class GeneralStatus(BaseModel):
    firmware_language: int
    firmware_release: str
    hardware_release: str
    vocabulary_language: Optional[int]
    vocabulary_release: Optional[str]
    control_panel_type: str
    general_standby: bool
    general_alarm_failure: bool
    general_low_battery: bool
    general_power_failure: bool
    general_tamper: bool
    wireless_failure: bool
    hold_up_status: bool
    technical_status: bool
    chime_status: bool
    pstn_status: bool
    general_pre_alarm: bool
    pgm_logical_output: bool
    access_denied: bool
    program_alarm: bool
    system_status_ok: bool
    gsm_status: bool
    general_tamper_alarm: bool
    general_failure_alarm: bool
    false_code_alarm: bool
    false_key_alarm: bool
    general_supervision_alarm: bool
    general_masking_alarm: bool
    general_hold_up_alarm: bool
    general_technical_alarm: bool
    general_memory_alarm: bool
    active_exit_time: bool
    control_panel_maintenance: bool
    outgoing_call: bool
    end_bypass_signaling: bool
    automatic_arming: bool
    general_isolation_status: bool
    masking_status: bool
    general_tamper_memory: bool
    failure_memory: bool
    false_code_memory: bool
    false_key_memory: bool
    low_battery_memory: bool
    power_failure_memory: bool
    pstn_memory: bool
    gsm_alarm_memory: bool
    voice_synthesis_board_present: bool
    incoming_call: bool
    internal_siren_status: bool
    external_siren_status: bool
    out1_status: bool
    out2_status: bool
    local_expansion_present: bool
    panic_alarm: bool
    internal_siren: bool
    external_siren: bool

    PANEL_TYPE_MAP: ClassVar[dict[int, str]] = {35: "TP20-440", 45: "TP8-88 PLUS", 49: "EV 10-50"}

    @classmethod
    def from_bytes(cls, data: bytes) -> "GeneralStatus":
        if len(data) != 16:
            raise ValueError("Response data must be exactly 16 bytes.")
        def _decode_release(release_byte: int) -> str:
            major = (release_byte >> 4) & 0x0F
            minor = release_byte & 0x0F
            return f"{major}.{minor}"
        return cls(
            firmware_language=data[0],
            firmware_release=_decode_release(data[1]),
            hardware_release=_decode_release(data[2]),
            vocabulary_language=data[3] if data[3] != 0xFF else None,
            vocabulary_release=_decode_release(data[4]) if data[3] != 0xFF else None,
            control_panel_type=cls.PANEL_TYPE_MAP.get(data[5], "Unknown"),
            general_standby=bool(data[8] & 0b00000001),
            general_alarm_failure=bool(data[8] & 0b00000010),
            general_low_battery=bool(data[8] & 0b00000100),
            general_power_failure=bool(data[8] & 0b00001000),
            general_tamper=bool(data[8] & 0b00010000),
            wireless_failure=bool(data[8] & 0b00100000),
            hold_up_status=bool(data[8] & 0b01000000),
            technical_status=bool(data[8] & 0b10000000),
            chime_status=bool(data[9] & 0b00000001),
            pstn_status=bool(data[9] & 0b00000010),
            general_pre_alarm=bool(data[9] & 0b00000100),
            pgm_logical_output=bool(data[9] & 0b00001000),
            access_denied=bool(data[9] & 0b00010000),
            program_alarm=bool(data[9] & 0b00100000),
            system_status_ok=bool(data[9] & 0b01000000),
            gsm_status=bool(data[9] & 0b10000000),
            general_tamper_alarm=bool(data[10] & 0b00000001),
            general_failure_alarm=bool(data[10] & 0b00000010),
            false_code_alarm=bool(data[10] & 0b00000100),
            false_key_alarm=bool(data[10] & 0b00001000),
            general_supervision_alarm=bool(data[10] & 0b00010000),
            general_masking_alarm=bool(data[10] & 0b00100000),
            general_hold_up_alarm=bool(data[10] & 0b01000000),
            general_technical_alarm=bool(data[10] & 0b10000000),
            general_memory_alarm=bool(data[11] & 0b00000001),
            active_exit_time=bool(data[11] & 0b00000010),
            control_panel_maintenance=bool(data[11] & 0b00000100),
            outgoing_call=bool(data[11] & 0b00001000),
            end_bypass_signaling=bool(data[11] & 0b00010000),
            automatic_arming=bool(data[11] & 0b00100000),
            general_isolation_status=bool(data[11] & 0b01000000),
            masking_status=bool(data[11] & 0b10000000),
            general_tamper_memory=bool(data[12] & 0b00000001),
            failure_memory=bool(data[12] & 0b00000010),
            false_code_memory=bool(data[12] & 0b00000100),
            false_key_memory=bool(data[12] & 0b00001000),
            low_battery_memory=bool(data[12] & 0b00100000),
            power_failure_memory=bool(data[12] & 0b01000000),
            pstn_memory=bool(data[12] & 0b10000000),
            gsm_alarm_memory=bool(data[13] & 0b00000001),
            voice_synthesis_board_present=bool(data[13] & 0b00000010),
            incoming_call=bool(data[13] & 0b00000100),
            internal_siren_status=bool(data[13] & 0b00001000),
            external_siren_status=bool(data[13] & 0b00010000),
            out1_status=bool(data[13] & 0b00100000),
            out2_status=bool(data[13] & 0b01000000),
            local_expansion_present=bool(data[13] & 0b10000000),
            panic_alarm=bool(data[14] & 0b00000001),
            internal_siren=bool(data[14] & 0b00000010),
            external_siren=bool(data[14] & 0b00000100),
        )

    def __hash__(self) -> int:
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


class ProgramStatus(BaseModel):
    program_status: ProgramStatusEnum
    prealarm: bool
    alarm: bool
    alarm_memory: bool
    reserved: bool
    idx: int
    name: Optional[str] = None

    @classmethod
    def from_bytes(cls, status_byte: int, idx: int) -> "ProgramStatus":
        return cls(
            program_status=ProgramStatusEnum(status_byte & 0x0F),
            prealarm=bool(status_byte & 0x10),
            alarm=bool(status_byte & 0x20),
            alarm_memory=bool(status_byte & 0x40),
            reserved=bool(status_byte & 0x80),
            idx=idx,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.program_status,
                self.prealarm,
                self.alarm,
                self.alarm_memory,
                self.reserved,
                self.idx,
                self.name,
            )
        )
    
    @property
    def is_active(self) -> bool:
        """Return True if the program is in any state other than STANDBY."""
        return self.program_status != ProgramStatusEnum.STANDBY
