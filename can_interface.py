import can

class CanInterface:
    def __init__(self, interface='virtual', channel='vcan0', bitrate=500000):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.bus = None

    def connect(self):
        try:
            self.bus = can.interface.Bus(channel=self.channel, bustype=self.interface, bitrate=self.bitrate)
            print(f"Connected to CAN interface {self.interface} on channel {self.channel} at {self.bitrate} bps.")
        except Exception as e:
            print(f"Failed to connect to CAN interface: {e}")
            self.bus = None

    def disconnect(self):
        if self.bus:
            self.bus.shutdown()
            print(f"Disconnected from CAN interface {self.interface} on channel {self.channel}.")
            self.bus = None
        else:
            print("No active CAN connection to disconnect.")
    
    def send_message(self, message_id, data):
        if not self.bus:
            print("No active CAN connection. Please connect first.")
            return
        
        msg = can.Message(arbitration_id=message_id, data=data, is_extended_id=False)
        try:
            self.bus.send(msg)
            print(f"Message sent: ID={hex(message_id)}, Data={data.hex()}")
        except can.CanError as e:
            print(f"Failed to send message: {e}")
            
    def receive_message(self, timeout=1):
        if not self.bus:
            print("No active CAN connection. Please connect first.")
            return
        
        try:
            msg = self.bus.recv(timeout)
            if msg:
                print(f"Message received: ID={hex(msg.arbitration_id)}, Data={msg.data.hex()}")
                return msg
            else:
                print("No message received within the timeout period.")
        except can.CanError as e:
            print(f"Failed to receive message: {e}")
            return None


