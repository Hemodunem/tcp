import json


def packet(packet_type, payload):
    return {
        "type": packet_type,
        "payload": payload
    }


def serialize(data):
    return bytes(json.dumps(data), "utf8")


def unserialize(buffer):
    return json.loads(buffer.decode("utf8"))


def message_packet(text):
    return serialize(
        packet("message", {
            "text": text
        })
    )

def file_packet():
    return serialize(
        packet("file", {

        })
    )
