from flask import Blueprint, jsonify, request

bp = Blueprint('redfish', __name__, url_prefix='/redfish/v1')

DEVICE_REGISTRY = {}

@bp.route('/Devices', methods=['GET'])
def list_devices():
    return jsonify({"Members": list(DEVICE_REGISTRY.values())})

@bp.route('/Telemetry/<device_id>', methods=['GET'])
def telemetry(device_id):
    device = DEVICE_REGISTRY.get(device_id)
    if not device:
        return jsonify({"error":"not found"}), 404
    return jsonify({"id": device_id, "telemetry": device.get("telemetry", {})})

@bp.route('/Actions/OTA.Update', methods=['POST'])
def trigger_ota():
    body = request.get_json()
    return jsonify({"status":"queued", "body": body})
