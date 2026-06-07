import asyncio
import random
import toga
from toga.style import Pack
from toga.style.pack import BOLD, COLUMN, ROW

BG_COLOR = "#0D0D0D"
CARD_COLOR = "#1C1C1E"
TEXT_MUTED = "#666666"
TEXT_LIGHT = "#F5F5F5"


class euc_app(toga.App):
    def startup(self):
        self.telemetry_data = {
            "speed": 0.0,
            "voltage": 12.6,
            "current": 1.5,
            "temperature": 35.2,
            "status": "Disconnected",
        }

        root_box = toga.Box(
            style=Pack(direction=COLUMN, flex=1, background_color=BG_COLOR)
        )

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

        self.lbl_speed = self._make_value_label("0.0 km/h")
        self.lbl_voltage = self._make_value_label("12.6 V")
        self.lbl_current = self._make_value_label("1.5 A")
        self.lbl_temp = self._make_value_label("35.2 °C")

        main_box.add(self._make_card("SPEED", self.lbl_speed))
        main_box.add(self._make_card("BATTERY VOLTAGE", self.lbl_voltage))
        main_box.add(self._make_card("CURRENT DRAW", self.lbl_current))
        main_box.add(self._make_card("TEMPERATURE", self.lbl_temp))

        root_box.add(main_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = root_box
        self.main_window.show()

        self._android_fullscreen()
        self.add_background_task(self._simulated_bluetooth_stream)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _make_value_label(self, text):
        return toga.Label(
            text,
            style=Pack(
                font_size=28,
                font_weight=BOLD,
                color=TEXT_LIGHT,
                # IMPORTANT: every child gets the same CARD_COLOR so it blends
                # with the card background. Because Toga on Android puts all
                # widgets in a single flat RelativeLayout, setClipToOutline on
                # the card box cannot clip its "children" — they are siblings
                # in the native view tree. The only reliable approach is to
                # make child backgrounds match the card, and draw the rounded
                # rect shape purely as the card's own background drawable.
                background_color=CARD_COLOR,
            ),
        )

    def _make_card(self, title_text, value_label):
        """
        Build a metric card with true rounded corners on Android.

        Because Toga's Android backend is a flat RelativeLayout — all Toga
        widgets are siblings at the native level regardless of logical Box
        nesting — setClipToOutline() on the card's native View has nothing to
        clip (child widgets are not native children of the card view).

        The correct approach:
          1. Set a GradientDrawable with rounded corners as the card background.
          2. Give EVERY child widget the same CARD_COLOR background so they
             visually sit inside the card (no white corners poking out).
          3. Do NOT call setClipToOutline — it provides no benefit here and
             was causing the misaligned-pixel artefacts.
          4. Use a post-layout ViewTreeObserver callback so the drawable is
             applied after Toga has measured and positioned the view, giving
             us the correct width/height for the outline if ever needed later.
        """
        card = toga.Box(
            style=Pack(
                direction=COLUMN,
                padding=14,
                margin_bottom=10,
                background_color=CARD_COLOR,
            )
        )

        lbl_title = toga.Label(
            title_text,
            style=Pack(
                font_size=10,
                font_weight=BOLD,
                color=TEXT_MUTED,
                padding_bottom=4,
                background_color=CARD_COLOR,  # must match card
            ),
        )

        value_row = toga.Box(
            style=Pack(direction=ROW, background_color=CARD_COLOR)
        )
        value_row.add(value_label)

        card.add(lbl_title)
        card.add(value_row)

        self._apply_android_card_bg(card)
        return card

    def _apply_android_card_bg(self, box):
        """
        Apply a rounded-rectangle background drawable to the card's native view.

        Key insight (from toga#3118 / toga#3235):
          Toga Android uses a *flat* native hierarchy — all widgets share one
          RelativeLayout container. The card Box's native view therefore has NO
          native children, so setClipToOutline does nothing useful and
          introduced the sub-pixel misalignment. We skip it entirely.

        What we do instead:
          - Read density from DisplayMetrics on the view's own context.
          - Round the dp→px conversion to a whole pixel.
          - Set a GradientDrawable (no stroke) as the view background.
          - Register a one-shot OnGlobalLayoutListener so the drawable is
            applied only after Toga has completed layout measurement, ensuring
            the view has non-zero width/height at apply time.
        """
        try:
            from android.graphics.drawable import GradientDrawable
            from android.graphics import Color
            from android.view import ViewTreeObserver

            native = box._impl.native

            def apply_bg():
                try:
                    dm = native.getContext().getResources().getDisplayMetrics()
                    density = dm.density
                except Exception:
                    density = 2.75  # FHD+ (1080×2340) fallback

                # 18 dp rounded to nearest whole pixel — no fractional blur
                radius_px = float(round(18 * density))

                shape = GradientDrawable()
                shape.setShape(GradientDrawable.RECTANGLE)
                shape.setColor(Color.parseColor(CARD_COLOR))
                # No setStroke() — a stroke would add border pixels that shift
                # the visual corner position relative to the fill edge.
                shape.setCornerRadius(radius_px)
                native.setBackground(shape)
                # Do NOT call setClipToOutline — Toga's flat view hierarchy
                # means there are no native children inside this view to clip.

            class LayoutListener(ViewTreeObserver.OnGlobalLayoutListener):
                def onGlobalLayout(self):
                    apply_bg()
                    # Remove self so we only fire once
                    try:
                        native.getViewTreeObserver().removeOnGlobalLayoutListener(self)
                    except Exception:
                        pass

            vto = native.getViewTreeObserver()
            if vto.isAlive():
                vto.addOnGlobalLayoutListener(LayoutListener())
            else:
                # Fallback: apply immediately
                apply_bg()

        except (ImportError, AttributeError, Exception):
            pass  # Desktop — no-op

    def _android_fullscreen(self):
        """Hide ActionBar and make the status bar match the app background."""
        try:
            from android.view import View, WindowManager
            from android.graphics.drawable import ColorDrawable
            from android.graphics import Color

            activity = self._impl.native

            try:
                ab = activity.getActionBar()
                if ab:
                    ab.hide()
            except Exception:
                pass

            try:
                sab = activity.getSupportActionBar()
                if sab:
                    sab.hide()
            except Exception:
                pass

            window = activity.getWindow()
            window.setBackgroundDrawable(ColorDrawable(Color.parseColor(BG_COLOR)))
            window.getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            )
            window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
            window.setStatusBarColor(Color.parseColor(BG_COLOR))

        except (ImportError, AttributeError, Exception):
            pass

    # ── Background task ──────────────────────────────────────────────────────

    async def _simulated_bluetooth_stream(self, app):
        await asyncio.sleep(1)
        self.status_label.text = "● Connected — Simulating BT Stream"

        while True:
            spd = round(random.uniform(24.5, 25.5), 2)
            vlt = round(random.uniform(82.5, 83.5), 2)
            cur = round(random.uniform(15, 20), 2)
            tmp = round(random.uniform(30.0, 32.0), 2)

            self.telemetry_data.update(speed=spd, voltage=vlt, current=cur, temperature=tmp)

            self.lbl_speed.text = f"{spd} km/h"
            self.lbl_voltage.text = f"{vlt} V"
            self.lbl_current.text = f"{cur} A"
            self.lbl_temp.text = f"{tmp} °C"

            await asyncio.sleep(0.5)


def main():
    return euc_app("EUC Telemetry", "com.example.euc_app")
