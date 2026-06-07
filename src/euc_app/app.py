import asyncio
import random
import toga
from toga.style import Pack
from toga.style.pack import BOLD, COLUMN, LEFT, ROW
from toga.colors import GREEN, BLUE, RED, ORANGE, GRAY

# 🎨 DESIGN CONFIGURATION
BG_COLOR = "#1A1A1A"       # Main background canvas
CARD_COLOR = "#262626"     # Dark gray for metric blocks
TEXT_MUTED = "#888888"     # Muted gray text for status/titles
TEXT_LIGHT = "#FFFFFF"     # Crisp white text


class euc_app(toga.App):

    def startup(self):
        # Dictionary holding state
        self.telemetry_data = {
            "speed": 0.0,
            "voltage": 12.6,
            "current": 1.5,
            "temperature": 35.2,
            "status": "Disconnected",
        }

        # 🛠️ FIXED: Remove Android White Outline Framework Padding
        # We enforce zero margin leaks on the root container so it completely bleeds to the edges
        main_box = toga.Box(
            style=Pack(
                direction=COLUMN, 
                padding=16,
                background_color=BG_COLOR, 
                flex=1
            )
        )

        # Title Section
        title_label = toga.Label(
            "Begode A1 LongRange",
            style=Pack(font_size=22, font_weight=BOLD, padding_bottom=4, color=TEXT_LIGHT, background_color=BG_COLOR)
        )
        self.status_label = toga.Label(
            f"Status: {self.telemetry_data['status']}",
            style=Pack(font_size=11, font_style="italic", padding_bottom=16, color=TEXT_MUTED, background_color=BG_COLOR)
        )

        main_box.add(title_label)
        main_box.add(self.status_label)

        # 4 Metric fields matching your layout framework
        self.lbl_speed = toga.Label(
            "0.0 km/h", style=Pack(font_size=24, font_weight=BOLD, color=TEXT_LIGHT, background_color=CARD_COLOR)
        )
        row1 = self.make_metric_row("Speed:", self.lbl_speed)

        self.lbl_voltage = toga.Label(
            "12.6 V", style=Pack(font_size=24, font_weight=BOLD, color=TEXT_LIGHT, background_color=CARD_COLOR)
        )
        row2 = self.make_metric_row("Battery Voltage:", self.lbl_voltage)

        self.lbl_current = toga.Label(
            "1.5 A", style=Pack(font_size=24, font_weight=BOLD, color=TEXT_LIGHT, background_color=CARD_COLOR)
        )
        row3 = self.make_metric_row("Current Draw:", self.lbl_current)

        self.lbl_temp = toga.Label(
            "35.2 °C", style=Pack(font_size=24, font_weight=BOLD, color=TEXT_LIGHT, background_color=CARD_COLOR)
        )
        row4 = self.make_metric_row("Temperature:", self.lbl_temp)

        main_box.add(row1)
        main_box.add(row2)
        main_box.add(row3)
        main_box.add(row4)

        # Main window setup
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        
        self.main_window.show()

        # 🚀 FIX: Native System Tweak (Hide Top Bar & Force Seamless Background)
        try:
            from org.beeware.android import MainActivity
            activity = MainActivity.setContext
            
            # 1. Hide the white/teal native Android Action Bar header completely
            action_bar = activity.getActionBar()
            if action_bar:
                action_bar.hide()
                
            # 2. Force the window wrapper background layout to match our canvas color
            # This completely kills off the white border leaks!
            from android.graphics.drawable import ColorDrawable
            from android.graphics import Color
            activity.getWindow().setBackgroundDrawable(ColorDrawable(Color.parseColor(BG_COLOR)))
        except (ImportError, AttributeError):
            pass

        # Kick off background data simulation loop
        self.add_background_task(self.simulated_bluetooth_stream)

    def make_metric_row(self, title_text, value_label):
        """Helper to create a row block layout with 30px uniform rounded corners."""
        row_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                padding=12,
                margin_bottom=14,  
                background_color=CARD_COLOR,
            )
        )

        title_label = toga.Label(
            title_text,
            style=Pack(
                font_size=13, color=TEXT_MUTED, font_weight=BOLD, padding_bottom=4, background_color=CARD_COLOR
            ),
        )

        value_container = toga.Box(
            style=Pack(direction=ROW, background_color=CARD_COLOR)
        )
        value_container.add(value_label)

        row_box.add(title_label)
        row_box.add(value_container)

        # ✨ FIXED: Native Android Uniform Corner Radius Matrix
        try:
            from android.graphics.drawable import GradientDrawable
            from android.graphics import Color
            
            shape = GradientDrawable()
            shape.setShape(GradientDrawable.RECTANGLE)
            shape.setColor(Color.parseColor(CARD_COLOR))
            
            # R, G, B, A array style - specifying exact pairs of (X-radius, Y-radius) 
            # for Top-Left, Top-Right, Bottom-Right, Bottom-Left to prevent stretching bugs.
            r = 30.0
            corner_radii = [r, r, r, r, r, r, r, r]
            shape.setCornerRadii(corner_radii)
            
            row_box._impl.native.setBackground(shape)
        except (ImportError, AttributeError):
            pass

        return row_box

    async def simulated_bluetooth_stream(self, app):
        """Asynchronous background data simulation loop."""
        await asyncio.sleep(1)
        self.status_label.text = "Status: Simulating Bluetooth Stream..."

        while True:
            self.telemetry_data["speed"] = round(random.uniform(20.0, 65.5), 1)
            self.telemetry_data["voltage"] = round(random.uniform(11.8, 12.6), 2)
            self.telemetry_data["current"] = round(random.uniform(5.0, 22.1), 1)
            self.telemetry_data["temperature"] = round(random.uniform(34.0, 42.0), 1)

            self.lbl_speed.text = f"{self.telemetry_data['speed']} km/h"
            self.lbl_voltage.text = f"{self.telemetry_data['voltage']} V"
            self.lbl_current.text = f"{self.telemetry_data['current']} A"
            self.lbl_temp.text = f"{self.telemetry_data['temperature']} °C"

            await asyncio.sleep(1)


def main():
    return euc_app("EUC Telemetry", "com.example.euc_app")
