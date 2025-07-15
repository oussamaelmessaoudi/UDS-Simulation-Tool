
def clean_hex(value):
    return value.replace("0x","").replace(" ", "").upper()

def build_diagnostic_session_control(params):
    sub_function = clean_hex(params.get("sub_function", "01"))
    return bytes.fromhex("10" + sub_function)

def build_ecu_reset(params):
    sub_function = clean_hex(params.get("sub_function", "01"))
    return bytes.fromhex("11" + sub_function)

def build_read_data_by_identifier(params):
    identifier = clean_hex(params.get("identifier", "F190"))
    return bytes.fromhex("22" + identifier)

def build_clear_dtcs(params):
    dtc_group = clean_hex(params.get("group", "FFFFFF"))
    return bytes.fromhex("14" + dtc_group)

service_dispatch = {
    "0x10": build_diagnostic_session_control,
    "0x11": build_ecu_reset,
    "0x14": build_clear_dtcs,
    "0x22": build_read_data_by_identifier,
    # Don't forget to add more services as needed
}
