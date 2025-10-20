from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Select, Static, TextArea

from textual_jumper import Jumper


class DemoJumpApp(App):
    """A demo application showcasing the Jumper widget functionality."""

    BINDINGS = [Binding("ctrl+o", "show_overlay", "Jump")]
    CSS = """
    #content {
        height: 100%;
        padding: 1 2;
    }

    .section {
        height: auto;
        border: solid $primary;
        padding: 1 2;
        margin: 1 0;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    Input {
        margin: 1 0;
    }

    TextArea {
        height: 10;
        margin: 1 0;
    }

    #info {
        background: $panel;
        height: auto;
        padding: 1 2;
        border: solid $accent;
        margin: 1 0;
    }

    #info Static {
        color: $text;
    }

    Button {
        margin: 1 1;
        min-width: 20;
    }

    Select {
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the demo app layout.

        Yields:
            Widgets for the demo application.
        """
        yield Header()
        yield Footer()
        self.jumper = Jumper()
        yield self.jumper

        with VerticalScroll(id="content"):
            with Vertical(id="info"):
                yield Static("🎯 Jumper Demo - Press [b]Ctrl+O[/b] to activate jump mode")
                yield Static("Then press a letter key to jump to that widget, or [b]Escape[/b] to cancel")

            with Vertical(classes="section"):
                yield Static("Personal Information", classes="section-title")
                first_name = Input(placeholder="First name")
                first_name.jump_mode = "focus"  # type: ignore
                yield first_name

                last_name = Input(placeholder="Last name")
                last_name.jump_mode = "focus"  # type: ignore
                yield last_name

                email = Input(placeholder="Email address")
                email.jump_mode = "focus"  # type: ignore
                yield email

                country_select = Select(
                    [("United States", "us"), ("Canada", "ca"), ("United Kingdom", "uk"), ("Germany", "de")],
                    prompt="Select country",
                )
                country_select.jump_mode = "click"  # type: ignore
                yield country_select

            with Horizontal(classes="section"):
                with Vertical():
                    yield Static("Address", classes="section-title")
                    street = Input(placeholder="Street")
                    street.jump_mode = "focus"  # type: ignore
                    yield street

                    city = Input(placeholder="City")
                    city.jump_mode = "focus"  # type: ignore
                    yield city

                with Vertical():
                    yield Static("Additional", classes="section-title")
                    state = Input(placeholder="State")
                    state.jump_mode = "focus"  # type: ignore
                    yield state

                    zip_code = Input(placeholder="ZIP code")
                    zip_code.jump_mode = "focus"  # type: ignore
                    yield zip_code

            with Vertical(classes="section"):
                yield Static("Comments", classes="section-title")
                comments = TextArea()
                comments.jump_mode = "focus"  # type: ignore
                yield comments

            with Vertical(classes="section"):
                yield Static("Additional Notes", classes="section-title")
                notes = TextArea()
                notes.jump_mode = "focus"  # type: ignore
                yield notes

            with Vertical(classes="section"):
                yield Static("Actions (Click Mode)", classes="section-title")
                yield Static("These buttons use jump_mode='click' - they will be clicked when jumped to")

                submit_btn = Button("Submit Form", variant="success", id="submit")
                submit_btn.jump_mode = "click"  # type: ignore
                yield submit_btn

                cancel_btn = Button("Cancel", variant="error", id="cancel")
                cancel_btn.jump_mode = "click"  # type: ignore
                yield cancel_btn

    def action_show_overlay(self) -> None:
        self.jumper.show()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        if button_id == "submit":
            self.notify("✓ Form submitted!", severity="information")
        elif button_id == "cancel":
            self.notify("✗ Form cancelled!", severity="warning")


def main() -> None:
    app = DemoJumpApp()
    app.run()
