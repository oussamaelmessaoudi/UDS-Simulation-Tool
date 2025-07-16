import can

bus = can.interface.Bus(channel='vcan0', bustype='socketcan', bitrate=500000)

while True:
    msg = bus.recv()
    if msg:
        print(f"Received message: ID={hex(msg.arbitration_id)}, Data={msg.data.hex()}")

        if msg.data[0] == 0x22:
            response = can.Message(arbitration_id=0x7E8, data=bytearray([0x62, msg.data[1], msg.data[2], 0x12, 0x34, 0x56]), is_extended_id=False)
            bus.send(response)
