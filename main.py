from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
import sys

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("UDS Simulator")

layout = QVBoxLayout()
label = QLabel("Welcome to UDS Simulator")
layout.addWidget(label)

window.setLayout(layout)
window.show()

sys.exit(app.exec())
