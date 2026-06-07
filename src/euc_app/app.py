import asyncio
import random
import toga
from toga.style import Pack
from toga.style.pack import BOLD, COLUMN, ROW

BG_COLOR = "#0D0D0D"
CARD_COLOR = "#1C1C1E"
ACCENT = "#444444"
TEXT_MUTED = "#666666"
TEXT_LIGHT = "#F5F5F5"
TEXT_DIM = "#AAAAAA"


class euc_app(toga.App):
    def startup(self):
        self.telemetry_data = {
            "speed": 0.0,
            "voltage": 12.6,
            "current": 1.5,
            "temperature": 35.2,
            "status": "Disconnected",
        }

        # Root box — full background, no margin/padding leaking white
        root_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                flex=1,
                background_color=BG_COLOR,
            )
        )

        # Inner content box with padding
        main_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                padding_top=48,
                padding_left=16,
                padding_right=16,
                padding_bottom=16,
                flex=1,
                background_color=BG_COLOR,
            )
        )

        # Header
        title_label = toga.Label(
            "Begode A1 LongRange",
            style=Pack(
                font_size=20,
                font_weight=BOLD,
                padding_bottom=2,
                color=TEXT_LIGHT,
                background_color=BG_COLOR,
            ),
        )
        self.status_label = toga.Label(
            f"● {self.telemetry_data['status']}",
            style=Pack(
                font_size=11,
                padding_bottom=20,
                color=TEXT_MUTED,
                background_color=BG_COLOR,
            ),
        )

        main_box.add(title_label)
        main_box.add(self.status_label)

        # Metric cards
        self.lbl_speed = self._make_value_label("0.0 km/h")
        self.lbl_voltage = self._make_value_label("12.6 V")
        self.lbl_current = self._make_value_label("1.5 A")
        self.lbl_temp = self._make_value_label("35.2 °C")

        main_box.add(self._make_card("SPEED", self.lbl_speed, is_hero=True))
        main_box.add(self._make_card("BATTERY VOLTAGE", self.lbl_voltage))
        main_box.add(self._make_card("CURRENT DRAW", self.lbl_current))
        main_box.add(self._make_card("TEMPERATURE", self.lbl_temp))

        root_box.add(main_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = root_box
        self.main_window.show()

        # ── Android-specific tweaks ──────────────────────────────────────────
        self._android_fullscreen()

        # ── Start simulated stream ───────────────────────────────────────────
        self.add_background_task(self._simulated_bluetooth_stream)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _make_value_label(self, text):
        return toga.Label(
            text,
            style=Pack(
                font_size=28,
                font_weight=BOLD,
                color=TEXT_LIGHT,
                background_color=CARD_COLOR,
            ),
        )

    def _make_card(self, title_text, value_label, is_hero=False):
        """Build a metric card. Rounded corners applied natively on Android."""
        card = toga.Box(
            style=Pack(
                direction=COLUMN,
                padding=14,
                margin_bottom=10,
                background_color=CARD_COLOR,
            )
        )

        accent_bar = toga.Box(
            style=Pack(
                height=2,
                width=32,
                padding_bottom=8,
                background_color=ACCENT,
            )
        )

        lbl_title = toga.Label(
            title_text,
            style=Pack(
                font_size=10,
                font_weight=BOLD,
                color=TEXT_MUTED,
                padding_bottom=4,
                background_color=CARD_COLOR,
            ),
        )

        value_row = toga.Box(
            style=Pack(direction=ROW, background_color=CARD_COLOR)
        )
        value_row.add(value_label)

        card.add(accent_bar)
        card.add(lbl_title)
        card.add(value_row)

        # Android: apply rounded rect background so corners are actually clipped
        self._apply_android_card_bg(card)

        return card

    def _apply_android_card_bg(self, box):
        """Apply a rounded rectangle background on Android using native APIs."""
        try:
            from android.graphics.drawable import GradientDrawable
            from android.graphics import Color

            shape = GradientDrawable()
            shape.setShape(GradientDrawable.RECTANGLE)
            shape.setColor(Color.parseColor(CARD_COLOR))

            # Convert 16dp → px using display density
            try:
                from android.content import Context
                ctx = self.main_window._impl.native.getContext()
                density = ctx.getResources().getDisplayMetrics().density
                radius = 16 * density
            except Exception:
                radius = 40.0  # fallback

            shape.setCornerRadius(radius)
            box._impl.native.setBackground(shape)
            box._impl.native.setClipToOutline(True)
        except (ImportError, AttributeError):
            pass  # Desktop / non-Android — no-op

    def _android_fullscreen(self):
        """Hide the ActionBar and status bar on Android, make background seamless."""
        try:
            from android.view import View, WindowManager
            from android.graphics.drawable import ColorDrawable
            from android.graphics import Color

            activity = self._impl.native  # the MainActivity

            # Hide ActionBar (the top title bar)
            action_bar = activity.getActionBar()
            if action_bar:
                action_bar.hide()

            # Also try AppCompat support action bar
            try:
                support_bar = activity.getSupportActionBar()
                if support_bar:
                    support_bar.hide()
            except Exception:
                pass

            window = activity.getWindow()

            # Remove white window background
            window.setBackgroundDrawable(
                ColorDrawable(Color.parseColor(BG_COLOR))
            )

            # Edge-to-edge: let content draw under status bar
            window.getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            )

            # Make status bar transparent so our dark bg shows through
            window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
            window.setStatusBarColor(Color.parseColor(BG_COLOR))

        except (ImportError, AttributeError, Exception):
            pass  # Desktop — silently skip

    # ── Background task ──────────────────────────────────────────────────────

    async def _simulated_bluetooth_stream(self, app):
        await asyncio.sleep(1)
        self.status_label.text = "● Connected — Simulating BT Stream"

        while True:
            spd = round(random.uniform(20.0, 65.5), 1)
            vlt = round(random.uniform(11.8, 12.6), 2)
            cur = round(random.uniform(5.0, 22.1), 1)
            tmp = round(random.uniform(34.0, 42.0), 1)

            self.telemetry_data.update(
                speed=spd, voltage=vlt, current=cur, temperature=tmp
            )

            self.lbl_speed.text = f"{spd} km/h"
            self.lbl_voltage.text = f"{vlt} V"
            self.lbl_current.text = f"{cur} A"
            self.lbl_temp.text = f"{tmp} °C"

            await asyncio.sleep(1)


def main():
    return euc_app("EUC Telemetry", "com.example.euc_app")
