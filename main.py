import sys
import json
import time
import threading
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from uds_controller import handle_service_request
class UDSSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.simulation_mode = False
        self.auto_tester_present = False
        self.can_connected = False
        self.log_data = []
        self.fake_responses = {}
        self.init_brutal_ui()
        self.setup_fake_responses()
        
    def init_brutal_ui(self):
        self.setWindowTitle("UDS BRUTAL SIMULATOR")
        self.setGeometry(100, 100, 1600, 1000)
        self.setStyleSheet("""
            QMainWindow { background: #0a0a0a; color: #00ff00; }
            QWidget { background: #0a0a0a; color: #00ff00; font-family: 'Consolas', monospace; }
            QPushButton { 
                background: #1a1a1a; 
                border: 2px solid #00ff00; 
                color: #00ff00; 
                padding: 8px; 
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background: #003300; }
            QPushButton:pressed { background: #00ff00; color: #000000; }
            QPushButton:disabled { background: #333; color: #666; border-color: #666; }
            QLineEdit { 
                background: #1a1a1a; 
                border: 2px solid #00ff00; 
                color: #00ff00; 
                padding: 6px; 
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QTextEdit { 
                background: #000000; 
                border: 2px solid #00ff00; 
                color: #00ff00; 
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            QComboBox { 
                background: #1a1a1a; 
                border: 2px solid #00ff00; 
                color: #00ff00; 
                padding: 6px;
                font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { color: #00ff00; }
            QLabel { color: #00ff00; font-weight: bold; }
            QGroupBox { 
                border: 2px solid #00ff00; 
                margin-top: 10px; 
                padding-top: 10px; 
                font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QStatusBar { background: #1a1a1a; color: #00ff00; border-top: 2px solid #00ff00; }
            QCheckBox { color: #00ff00; }
            QCheckBox::indicator:checked { background: #00ff00; }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        
        # Left panel - Controls
        left_panel = QVBoxLayout()
        
        # Service selection
        service_group = QGroupBox("SERVICE SELECTION")
        service_layout = QVBoxLayout()
        
        self.service_combo = QComboBox()
        self.service_combo.addItems([
            "0x10 - Diagnostic Session Control",
            "0x11 - ECU Reset", 
            "0x14 - Clear DTCs",
            "0x19 - Read DTCs",
            "0x22 - Read Data By Identifier",
            "0x23 - Read Memory By Address",
            "0x27 - Security Access",
            "0x28 - Communication Control",
            "0x2E - Write Data By Identifier",
            "0x31 - Routine Control",
            "0x34 - Request Download",
            "0x36 - Transfer Data",
            "0x37 - Request Transfer Exit",
            "0x3E - Tester Present",
            "0x85 - Control DTC Setting"
        ])
        
        service_layout.addWidget(self.service_combo)
        service_group.setLayout(service_layout)
        
        # Custom inputs
        input_group = QGroupBox("PARAMETERS")
        input_layout = QFormLayout()
        
        self.service_id_input = QLineEdit()
        self.service_id_input.setPlaceholderText("0x22")
        
        self.did_input = QLineEdit()
        self.did_input.setPlaceholderText("0xF190")
        
        self.subfunction_input = QLineEdit()
        self.subfunction_input.setPlaceholderText("0x01")
        
        self.payload_input = QLineEdit()
        self.payload_input.setPlaceholderText("Additional hex data")
        
        input_layout.addRow("Service ID:", self.service_id_input)
        input_layout.addRow("Data ID (DID):", self.did_input)
        input_layout.addRow("Sub-function:", self.subfunction_input)
        input_layout.addRow("Payload:", self.payload_input)
        
        input_group.setLayout(input_layout)
        
        # Send controls
        send_group = QGroupBox("EXECUTION")
        send_layout = QVBoxLayout()
        
        self.send_btn = QPushButton("SEND REQUEST")
        self.send_btn.clicked.connect(self.send_request)
        
        self.batch_btn = QPushButton("BATCH MODE")
        self.batch_btn.clicked.connect(self.batch_mode)
        
        self.replay_btn = QPushButton("REPLAY LAST")
        self.replay_btn.clicked.connect(self.replay_last)
        
        send_layout.addWidget(self.send_btn)
        send_layout.addWidget(self.batch_btn)
        send_layout.addWidget(self.replay_btn)
        
        send_group.setLayout(send_layout)
        
        # Simulation controls
        sim_group = QGroupBox("SIMULATION")
        sim_layout = QVBoxLayout()
        
        self.sim_toggle = QPushButton("SIMULATION: OFF")
        self.sim_toggle.clicked.connect(self.toggle_simulation)
        
        self.tester_present_toggle = QPushButton("TESTER PRESENT: OFF")
        self.tester_present_toggle.clicked.connect(self.toggle_tester_present)
        
        self.edit_responses_btn = QPushButton("EDIT RESPONSES")
        self.edit_responses_btn.clicked.connect(self.edit_responses)
        
        sim_layout.addWidget(self.sim_toggle)
        sim_layout.addWidget(self.tester_present_toggle)
        sim_layout.addWidget(self.edit_responses_btn)
        
        sim_group.setLayout(sim_layout)
        
        # CAN settings
        can_group = QGroupBox("CAN INTERFACE")
        can_layout = QFormLayout()
        
        self.interface_combo = QComboBox()
        self.interface_combo.addItems(["virtual", "socketcan", "usb", "peak", "vector"])
        
        self.channel_input = QLineEdit()
        self.channel_input.setText("vcan0")
        
        self.bitrate_input = QLineEdit()
        self.bitrate_input.setText("500000")
        
        self.connect_btn = QPushButton("CONNECT")
        self.connect_btn.clicked.connect(self.toggle_can_connection)
        
        can_layout.addRow("Interface:", self.interface_combo)
        can_layout.addRow("Channel:", self.channel_input)
        can_layout.addRow("Bitrate:", self.bitrate_input)
        can_layout.addRow("", self.connect_btn)
        
        can_group.setLayout(can_layout)
        
        # Add all groups to left panel
        left_panel.addWidget(service_group)
        left_panel.addWidget(input_group)
        left_panel.addWidget(send_group)
        left_panel.addWidget(sim_group)
        left_panel.addWidget(can_group)
        left_panel.addStretch()
        
        # Right panel - Response and logging
        right_panel = QVBoxLayout()
        
        # Response display
        response_group = QGroupBox("RESPONSE")
        response_layout = QVBoxLayout()
        
        self.response_text = QTextEdit()
        self.response_text.setMaximumHeight(200)
        self.response_text.setFont(QFont("Consolas", 11))
        
        response_layout.addWidget(self.response_text)
        response_group.setLayout(response_layout)
        
        # Log display
        log_group = QGroupBox("LOG")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 10))
        
        log_controls = QHBoxLayout()
        self.clear_log_btn = QPushButton("CLEAR")
        self.clear_log_btn.clicked.connect(self.clear_log)
        
        self.export_log_btn = QPushButton("EXPORT")
        self.export_log_btn.clicked.connect(self.export_log)
        
        self.save_config_btn = QPushButton("SAVE CONFIG")
        self.save_config_btn.clicked.connect(self.save_config)
        
        self.load_config_btn = QPushButton("LOAD CONFIG")
        self.load_config_btn.clicked.connect(self.load_config)
        
        log_controls.addWidget(self.clear_log_btn)
        log_controls.addWidget(self.export_log_btn)
        log_controls.addWidget(self.save_config_btn)
        log_controls.addWidget(self.load_config_btn)
        log_controls.addStretch()
        
        log_layout.addWidget(self.log_text)
        log_layout.addLayout(log_controls)
        log_group.setLayout(log_layout)
        
        right_panel.addWidget(response_group)
        right_panel.addWidget(log_group)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        
        # Status bar
        self.statusBar().showMessage("READY | SIMULATION: OFF | CAN: DISCONNECTED")
        
        # Auto-update service ID based on combo selection
        self.service_combo.currentTextChanged.connect(self.update_service_id)
        
        # Start tester present timer
        self.tester_present_timer = QTimer()
        self.tester_present_timer.timeout.connect(self.send_tester_present)
        
        self.last_request = None
        
    def setup_fake_responses(self):
        """Setup default fake ECU responses"""
        self.fake_responses = {
            "0x10": "50 01",  # Positive response for session control
            "0x11": "51 01",  # Positive response for ECU reset
            "0x14": "54",     # Positive response for clear DTCs
            "0x19": "59 02 AF 12 34 56",  # Positive response with fake DTC
            "0x22": "62 F1 90 31 32 33 34 35",  # Positive response with fake data
            "0x23": "63 12 34 56 78",  # Positive response for read memory
            "0x27": "67 01 12 34",  # Security access response
            "0x28": "68 01",  # Communication control response
            "0x2E": "6E F1 90",  # Write data response
            "0x31": "71 01",  # Routine control response
            "0x34": "74 10 0F",  # Request download response
            "0x36": "76 01",  # Transfer data response
            "0x37": "77",     # Request transfer exit response
            "0x3E": "7E 00",  # Tester present response
            "0x85": "C5 01"   # Control DTC setting response
        }
        
    def update_service_id(self, text):
        """Auto-update service ID field when combo changes"""
        service_id = text.split(" - ")[0]
        self.service_id_input.setText(service_id)
        
    def send_request(self):
        """Send UDS request"""
        service_id = self.service_id_input.text().strip()
        if not service_id:
            service_id = self.service_combo.currentText().split(" - ")[0]
            
        did = self.did_input.text().strip()
        subfunction = self.subfunction_input.text().strip()
        payload = self.payload_input.text().strip()
        
        # Build request
        params = {
            "sub_function": subfunction,
            "identifier": did,
            "payload": payload
        }
        
        try:
            request_bytes = handle_service_request(service_id, params)
            request = request_bytes.hex(" ").upper()
        except Exception as e:
            selfresponse_text.setHtml(f'<span style="color: #ff0000;">ERROR: {str(e)}</span>')
            return

        
        # Log request
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] TX: {request}"
        self.log_data.append(log_entry)
        self.log_text.append(f'<span style="color: #ffff00;">{log_entry}</span>')
        
        # Process response
        start_time = time.time()
        
        if self.simulation_mode:
            # Simulate response
            response = self.fake_responses.get(service_id, "7F " + service_id.replace("0x", "") + " 11")
            response_time = round((time.time() - start_time) * 1000, 2)
            
            # Log response
            log_entry = f"[{timestamp}] RX: {response} ({response_time}ms)"
            self.log_data.append(log_entry)
            
            if response.startswith("7F"):
                self.log_text.append(f'<span style="color: #ff0000;">{log_entry}</span>')
                self.response_text.setHtml(f'<span style="color: #ff0000;">NEGATIVE RESPONSE: {response}<br>Error: {self.get_error_description(response)}</span>')
            else:
                self.log_text.append(f'<span style="color: #00ff00;">{log_entry}</span>')
                self.response_text.setHtml(f'<span style="color: #00ff00;">POSITIVE RESPONSE: {response}<br>Decoded: {self.decode_response(service_id, response)}</span>')
        else:
            # Real CAN interface would go here
            response = "7F " + service_id.replace("0x", "") + " 31"  # Service not supported
            response_time = 50.0
            
            log_entry = f"[{timestamp}] RX: {response} ({response_time}ms)"
            self.log_data.append(log_entry)
            self.log_text.append(f'<span style="color: #ff0000;">{log_entry}</span>')
            self.response_text.setHtml(f'<span style="color: #ff0000;">NEGATIVE RESPONSE: {response}<br>Error: Service not supported (real CAN not implemented)</span>')
            
    def get_error_description(self, response):
        """Get error description from negative response"""
        error_codes = {
            "10": "General reject",
            "11": "Service not supported",
            "12": "Sub-function not supported",
            "13": "Incorrect message length",
            "14": "Response too long",
            "21": "Busy repeat request",
            "22": "Conditions not correct",
            "24": "Request sequence error",
            "25": "No response from sub-net component",
            "26": "Failure prevents execution",
            "31": "Request out of range",
            "33": "Security access denied",
            "35": "Invalid key",
            "36": "Exceed number of attempts",
            "37": "Required time delay not expired",
            "70": "Upload/download not accepted",
            "71": "Transfer data suspended",
            "72": "General programming failure",
            "73": "Wrong block sequence counter",
            "78": "Request correctly received - response pending",
            "7E": "Sub-function not supported in active session",
            "7F": "Service not supported in active session"
        }
        
        parts = response.split()
        if len(parts) >= 3:
            error_code = parts[2]
            return error_codes.get(error_code, f"Unknown error code: {error_code}")
        return "Unknown error"
        
    def decode_response(self, service_id, response):
        """Decode positive response"""
        decodings = {
            "0x10": "Session changed successfully",
            "0x11": "ECU reset initiated",
            "0x14": "DTCs cleared successfully",
            "0x19": "DTCs read successfully",
            "0x22": "Data read successfully",
            "0x23": "Memory read successfully",
            "0x27": "Security access response",
            "0x28": "Communication control set",
            "0x2E": "Data written successfully",
            "0x31": "Routine control executed",
            "0x34": "Download request accepted",
            "0x36": "Data transfer successful",
            "0x37": "Transfer exit successful",
            "0x3E": "Tester present acknowledged",
            "0x85": "DTC control set"
        }
        
        return decodings.get(service_id, "Response received")
        
    def toggle_simulation(self):
        """Toggle simulation mode"""
        self.simulation_mode = not self.simulation_mode
        if self.simulation_mode:
            self.sim_toggle.setText("SIMULATION: ON")
            self.statusBar().showMessage("SIMULATION: ON | CAN: DISCONNECTED")
        else:
            self.sim_toggle.setText("SIMULATION: OFF")
            self.statusBar().showMessage("SIMULATION: OFF | CAN: DISCONNECTED")
            
    def toggle_tester_present(self):
        """Toggle auto tester present"""
        self.auto_tester_present = not self.auto_tester_present
        if self.auto_tester_present:
            self.tester_present_toggle.setText("TESTER PRESENT: ON")
            self.tester_present_timer.start(2000)  # Every 2 seconds
        else:
            self.tester_present_toggle.setText("TESTER PRESENT: OFF")
            self.tester_present_timer.stop()
            
    def send_tester_present(self):
        """Send tester present automatically"""
        if self.auto_tester_present:
            old_service = self.service_id_input.text()
            self.service_id_input.setText("0x3E")
            self.subfunction_input.setText("0x00")
            self.send_request()
            self.service_id_input.setText(old_service)
            
    def toggle_can_connection(self):
        """Toggle CAN connection"""
        self.can_connected = not self.can_connected
        if self.can_connected:
            self.connect_btn.setText("DISCONNECT")
            self.statusBar().showMessage(f"CAN: CONNECTED ({self.channel_input.text()})")
        else:
            self.connect_btn.setText("CONNECT")
            self.statusBar().showMessage("CAN: DISCONNECTED")
            
    def batch_mode(self):
        """Open batch mode dialog"""
        dialog = BatchModeDialog(self)
        dialog.exec()
        
    def replay_last(self):
        """Replay last request"""
        if self.last_request:
            self.send_request()
            
    def edit_responses(self):
        """Edit fake ECU responses"""
        dialog = ResponseEditorDialog(self.fake_responses, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.fake_responses = dialog.get_responses()
            
    def clear_log(self):
        """Clear log display"""
        self.log_text.clear()
        self.log_data.clear()
        
    def export_log(self):
        """Export log to file"""
        filename, _ = QFileDialog.getSaveFileName(self, "Export Log", "", "Text Files (*.txt);;CSV Files (*.csv)")
        if filename:
            with open(filename, 'w') as f:
                for entry in self.log_data:
                    f.write(entry + "\n")
                    
    def save_config(self):
        """Save configuration"""
        config = {
            "fake_responses": self.fake_responses,
            "interface": self.interface_combo.currentText(),
            "channel": self.channel_input.text(),
            "bitrate": self.bitrate_input.text()
        }
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
                
    def load_config(self):
        """Load configuration"""
        filename, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                    
                self.fake_responses = config.get("fake_responses", self.fake_responses)
                self.interface_combo.setCurrentText(config.get("interface", "virtual"))
                self.channel_input.setText(config.get("channel", "vcan0"))
                self.bitrate_input.setText(config.get("bitrate", "500000"))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load config: {e}")

class BatchModeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BATCH MODE")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        self.batch_text = QTextEdit()
        self.batch_text.setPlaceholderText("Enter UDS commands, one per line:\n0x22 0xF190\n0x19 0x02\n0x10 0x03")
        layout.addWidget(self.batch_text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.execute_batch)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def execute_batch(self):
        """Execute batch commands"""
        commands = self.batch_text.toPlainText().strip().split('\n')
        for cmd in commands:
            if cmd.strip():
                # Execute each command
                pass
        self.accept()

class ResponseEditorDialog(QDialog):
    def __init__(self, responses, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EDIT FAKE RESPONSES")
        self.setModal(True)
        self.resize(600, 400)
        self.responses = responses.copy()
        
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Service", "Response"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        self.populate_table()
        layout.addWidget(self.table)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_responses)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def populate_table(self):
        """Populate table with current responses"""
        self.table.setRowCount(len(self.responses))
        for i, (service, response) in enumerate(self.responses.items()):
            self.table.setItem(i, 0, QTableWidgetItem(service))
            self.table.setItem(i, 1, QTableWidgetItem(response))
            
    def save_responses(self):
        """Save edited responses"""
        self.responses.clear()
        for i in range(self.table.rowCount()):
            service_item = self.table.item(i, 0)
            response_item = self.table.item(i, 1)
            if service_item and response_item:
                self.responses[service_item.text()] = response_item.text()
        self.accept()
        
    def get_responses(self):
        """Get updated responses"""
        return self.responses

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UDSSimulator()
    window.show()
    sys.exit(app.exec())
