from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textual_jumper.jumper import JumpInfo

from rich.text import Text
from textual.binding import Binding
from textual.events import Key
from textual.geometry import Offset
from textual.reactive import reactive
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
        width: auto;
    }
    """

    input_buffer: reactive[str] = reactive("")

    def __init__(self, key_text: str, *args: Any, **kwargs: Any) -> None:
        self.key_text = key_text
        super().__init__("", *args, **kwargs)

    def render(self) -> Text:
        """Render the label with typed characters in heavily dimmed grey."""
        result = Text()

        # Determine how many characters match the input buffer
        typed_len = len(self.input_buffer) if self.key_text.startswith(self.input_buffer) else 0

        # Render typed characters in heavily dimmed grey
        if typed_len > 0:
            result.append(self.key_text[:typed_len], style="dim #666666")

        # Render remaining characters in black (normal)
        if typed_len < len(self.key_text):
            result.append(self.key_text[typed_len:], style="bold black")

        return result


class JumpOverlay(ModalScreen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Close")]

    input_buffer: reactive[str] = reactive("", init=False)

    def __init__(self, overlays: dict[Offset, "JumpInfo"]) -> None:
        self.overlays = overlays
        super().__init__()

    def compose(self) -> Iterator[LetterLabel]:
        for offset, jump_info in self.overlays.items():
            label = LetterLabel(jump_info.key)
            label.offset = offset
            yield label

    def watch_input_buffer(self, new_buffer: str) -> None:
        """Update all labels when input buffer changes."""
        for label in self.query(LetterLabel):
            # Update the label's input buffer (data binding)
            label.input_buffer = new_buffer

            # Update visibility based on matching
            if new_buffer:
                label.display = label.key_text.startswith(new_buffer)
            else:
                label.display = True

    def on_key(self, event: Key) -> None:
        """Handle key press to jump to widget."""
        if not event.character:
            return

        # Add character to input buffer
        self.input_buffer += event.character

        # Check for exact match
        for jump_info in self.overlays.values():
            if jump_info.key == self.input_buffer:
                # Exact match found - jump to widget
                self._jump_to_widget(jump_info)
                return

        # Check if input buffer is a valid prefix
        has_matches = any(info.key.startswith(self.input_buffer) for info in self.overlays.values())

        if not has_matches:
            # No matches - clear buffer
            self.input_buffer = ""

    def _jump_to_widget(self, jump_info: "JumpInfo") -> None:
        """Jump to the widget specified by jump_info."""
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
