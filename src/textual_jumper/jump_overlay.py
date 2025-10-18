from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual_jumper.jumper import JumpInfo

from textual.binding import Binding
from textual.events import Key
from textual.geometry import Offset
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Label


class LetterLabel(Label):
    DEFAULT_CSS = """
    LetterLabel {
        dock:top;
        background:$warning;
        color:black;
        text-style: bold;
        padding: 0 1;
        margin-right: 1;
        offset-y: -1;
        height: 1;
        min-width: 3;
        width: 3;
    }
    """


class JumpOverlay(ModalScreen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Close")]

    def __init__(self, overlays: dict[Offset, "JumpInfo"]) -> None:
        self.overlays = overlays
        super().__init__()

    def compose(self) -> Iterator[LetterLabel]:
        for offset, jump_info in self.overlays.items():
            label = LetterLabel(jump_info.key)
            label.offset = offset
            yield label

    def on_mount(self) -> None:
        self.notify(f"{self.overlays}", markup=False)

    def on_key(self, event: Key) -> None:
        """Handle key press to jump to widget."""
        if not event.character:
            return

        # Find the jump info for this key
        for jump_info in self.overlays.values():
            if jump_info.key == event.character:
                # Get the widget
                if isinstance(jump_info.widget, Widget):
                    # Direct widget reference
                    widget = jump_info.widget
                else:
                    # Widget ID - query for it
                    try:
                        widget = self.app.query_one(f"#{jump_info.widget}")
                    except Exception:
                        # Widget not found, just dismiss
                        self.dismiss()
                        return

                # Dismiss the screen with the widget as return value
                self.dismiss(widget)
                return
