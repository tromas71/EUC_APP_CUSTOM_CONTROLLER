import flet as ft
import time
import threading
import random

# Global state dictionary to hold telemetry metrics
telemetry_data = {
    "voltage": 12.6,
    "temperature": 35.2,
    "speed": 0.0,
    "current": 1.5,
    "status": "Disconnected"
}

def main(page: ft.Page):
    page.title = "EV Telemetry Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 400
    page.window_height = 800  # Approximating a mobile screen layout

    # Define visual UI text elements
    lbl_voltage = ft.Text(f"{telemetry_data['voltage']} V", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_ACCENT_700)
    lbl_temp = ft.Text(f"{telemetry_data['temperature']} °C", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_ACCENT_400)
    lbl_speed = ft.Text(f"{telemetry_data['speed']} km/h", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_ACCENT_400)
    lbl_current = ft.Text(f"{telemetry_data['current']} A", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_ACCENT_400)
    lbl_status = ft.Text(f"Status: {telemetry_data['status']}", size=14, italic=True, color=ft.Colors.GREY_400)

    # Helper function to generate clean metric container cards
    def make_metric_card(title, icon, control_element):
        return ft.Card(
            expand=True,
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, size=20, color=ft.Colors.BLUE_GREY_200), 
                        ft.Text(title, size=14, color=ft.Colors.BLUE_GREY_200)
                    ]),
                    ft.Container(content=control_element, alignment=ft.Alignment.CENTER, padding=10)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        )

    # Dashboard Grid Structure
    dashboard_grid = ft.Column([
        ft.Text("Vehicle Telemetry", size=26, weight=ft.FontWeight.BOLD),
        lbl_status,
        ft.Divider(height=10, color=ft.Colors.SURFACE_CONTAINER_HIGHEST),
        
        # Row 1: Speed and Voltage
        ft.Row([
            make_metric_card("Speed", ft.Icons.SPEED, lbl_speed),
            make_metric_card("Battery Voltage", ft.Icons.ELECTRIC_BOLT, lbl_voltage)
        ], spacing=10),
        
        # Row 2: Current and Temperature
        ft.Row([
            make_metric_card("Current Draw", ft.Icons.ELECTRIC_METER, lbl_current),
            make_metric_card("Temperature", ft.Icons.THERMOSTAT, lbl_temp)
        ], spacing=10),
    ], spacing=15)

    page.add(dashboard_grid)

    # Background Monitoring Thread
    def simulated_bluetooth_stream():
        # Later on, initiate your bluetooth connection handshake here.
        telemetry_data["status"] = "Simulating Bluetooth Stream..."
        lbl_status.value = f"Status: {telemetry_data['status']}"
        page.update()

        while True:
            # Injecting mock telemetry changes over time
            telemetry_data["speed"] = round(random.uniform(20.0, 65.5), 1)
            telemetry_data["voltage"] = round(random.uniform(11.8, 12.6), 2)
            telemetry_data["current"] = round(random.uniform(5.0, 22.1), 1)
            telemetry_data["temperature"] = round(random.uniform(34.0, 42.0), 1)

            # Push updates smoothly to the UI rendering engine
            lbl_speed.value = f"{telemetry_data['speed']} km/h"
            lbl_voltage.value = f"{telemetry_data['voltage']} V"
            lbl_current.value = f"{telemetry_data['current']} A"
            lbl_temp.value = f"{telemetry_data['temperature']} °C"
            
            page.update()
            time.sleep(1)  # Refresh interval rate (1 second)

    # Spin up background execution context safely
    threading.Thread(target=simulated_bluetooth_stream, daemon=True).start()

# Modern Flet application launcher method
ft.run(main)