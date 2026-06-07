import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, BOLD
import threading
import time
import random

class EUCTelemetryApp(toga.App):
    def startup(self):
        # Dictionary holding state
        self.telemetry_data = {
            "speed": 0.0,
            "voltage": 12.6,
            "current": 1.5,
            "temperature": 35.2,
            "status": "Disconnected"
        }

        # Main containing Box (Vertical Stack)
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=16))

        # Title Section
        title_label = toga.Label(
            "Vehicle Telemetry",
            style=Pack(font_size=22, font_weight=BOLD, padding_bottom=4)
        )
        self.status_label = toga.Label(
            f"Status: {self.telemetry_data['status']}",
            style=Pack(font_size=11, font_style="italic", padding_bottom=12)
        )
        
        main_box.add(title_label)
        main_box.add(self.status_label)

        # 4 Separate Rows (Stacked Vertically)
        self.lbl_speed = toga.Label("0.0 km/h", style=Pack(font_size=24, font_weight=BOLD, color="#4caf50"))
        row1 = self.make_metric_row("Speed", self.lbl_speed)

        self.lbl_voltage = toga.Label("12.6 V", style=Pack(font_size=24, font_weight=BOLD, color="#2196f3"))
        row2 = self.make_metric_row("Battery Voltage", self.lbl_voltage)

        self.lbl_current = toga.Label("1.5 A", style=Pack(font_size=24, font_weight=BOLD, color="#f44336"))
        row3 = self.make_metric_row("Current Draw", self.lbl_current)

        self.lbl_temp = toga.Label("35.2 °C", style=Pack(font_size=24, font_weight=BOLD, color="#ff9800"))
        row4 = self.make_metric_row("Temperature", self.lbl_temp)

        # Add rows to layout
        main_box.add(row1)
        main_box.add(row2)
        main_box.add(row3)
        main_box.add(row4)

        # Main window setup
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        # Kickoff native safe background thread execution after startup completes
        threading.Thread(target=self.simulated_bluetooth_stream, daemon=True).start()

    def make_metric_row(self, title_text, value_label):
        """Helper to generate a clean, full-width 1-row dashboard component."""
        row_box = toga.Box(style=Pack(direction=COLUMN, padding=8, background_color="#1e1e1e"))
        title_label = toga.Label(title_text, style=Pack(font_size=11, color="#b0bec5", padding_bottom=4))
        
        # Center align components inside internal layout container
        align_container = toga.Box(style=Pack(direction=ROW, justify=CENTER))
        align_container.add(value_label)
        
        row_box.add(title_label)
        row_box.add(align_container)
        return row_box

    def simulated_bluetooth_stream(self):
        # Brief sleep interval allowing window threads to fully instantiate
        time.sleep(1)
        self.status_label.text = "Status: Simulating Bluetooth Stream..."

        while True:
            # Generate mock data
            self.telemetry_data["speed"] = round(random.uniform(20.0, 65.5), 1)
            self.telemetry_data["voltage"] = round(random.uniform(11.8, 12.6), 2)
            self.telemetry_data["current"] = round(random.uniform(5.0, 22.1), 1)
            self.telemetry_data["temperature"] = round(random.uniform(34.0, 42.0), 1)

            # Thread-safe interface modification via native properties updates
            self.lbl_speed.text = f"{self.telemetry_data['speed']} km/h"
            self.lbl_voltage.text = f"{self.telemetry_data['voltage']} V"
            self.lbl_current.text = f"{self.telemetry_data['current']} A"
            self.lbl_temp.text = f"{self.telemetry_data['temperature']} °C"

            time.sleep(1)

def main():
    return EUCTelemetryApp("EUC Telemetry", "org.example.euctelemetry")
