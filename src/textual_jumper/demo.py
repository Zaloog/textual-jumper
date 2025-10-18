from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Static, TextArea

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
                first_name.jumpable = True  # type: ignore
                yield first_name

                last_name = Input(placeholder="Last name")
                last_name.jumpable = True  # type: ignore
                yield last_name

                email = Input(placeholder="Email address")
                email.jumpable = True  # type: ignore
                yield email

            with Horizontal(classes="section"):
                with Vertical():
                    yield Static("Address", classes="section-title")
                    street = Input(placeholder="Street")
                    street.jumpable = True  # type: ignore
                    yield street

                    city = Input(placeholder="City")
                    city.jumpable = True  # type: ignore
                    yield city

                with Vertical():
                    yield Static("Additional", classes="section-title")
                    state = Input(placeholder="State")
                    state.jumpable = True  # type: ignore
                    yield state

                    zip_code = Input(placeholder="ZIP code")
                    zip_code.jumpable = True  # type: ignore
                    yield zip_code

            with Vertical(classes="section"):
                yield Static("Comments", classes="section-title")
                comments = TextArea()
                comments.jumpable = True  # type: ignore
                yield comments

            with Vertical(classes="section"):
                yield Static("Additional Notes", classes="section-title")
                notes = TextArea()
                notes.jumpable = True  # type: ignore
                yield notes

    def action_show_overlay(self) -> None:
        self.jumper.show()


def main() -> None:
    app = DemoJumpApp()
    app.run()
