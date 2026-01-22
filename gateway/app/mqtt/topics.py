def heartbeat_topic(device_id: str) -> str:
    return f"devices/{device_id}/heartbeat"

def status_topic(device_id: str) -> str:
    return f"devices/{device_id}/status"

def ota_topic(device_id: str) -> str:
    return f"devices/{device_id}/ota"

def ota_result_topic(device_id: str) -> str:
    return f"devices/{device_id}/ota/result"

