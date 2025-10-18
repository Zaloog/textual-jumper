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
        width: auto;
    }
    """


class JumpOverlay(ModalScreen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Close")]

    def __init__(self, overlays: dict[Offset, "JumpInfo"]) -> None:
        self.overlays = overlays
        self._input_buffer = ""
        super().__init__()

    def compose(self) -> Iterator[LetterLabel]:
        for offset, jump_info in self.overlays.items():
            label = LetterLabel(jump_info.key)
            label.offset = offset
            yield label

    def on_mount(self) -> None:
        # Show input buffer and matching keys
        self._update_display()

    def _update_display(self) -> None:
        """Update label visibility based on current input buffer."""
        if not self._input_buffer:
            # Show all labels
            message = "Type a key to jump"
        else:
            # Show current input
            matching_keys = [info.key for info in self.overlays.values() if info.key.startswith(self._input_buffer)]
            message = f"Input: {self._input_buffer} ({len(matching_keys)} matches)"

        self.notify(message, timeout=1)

        # Update label visibility/styling based on matching
        for label in self.query(LetterLabel):
            label_text = str(label.render())
            if self._input_buffer:
                # Hide non-matching labels
                if not label_text.startswith(self._input_buffer):
                    label.display = False
                else:
                    label.display = True
            else:
                label.display = True

    def on_key(self, event: Key) -> None:
        """Handle key press to jump to widget."""
        if not event.character:
            return

        # Add character to input buffer
        self._input_buffer += event.character

        # Check for exact match
        for jump_info in self.overlays.values():
            if jump_info.key == self._input_buffer:
                # Exact match found - jump to widget
                self._jump_to_widget(jump_info)
                return

        # Check if input buffer is a valid prefix
        has_matches = any(info.key.startswith(self._input_buffer) for info in self.overlays.values())

        if not has_matches:
            # No matches - clear buffer and show message
            self._input_buffer = ""
            self.notify("No matching keys", severity="warning", timeout=2)
            self._update_display()
        else:
            # Still have potential matches - update display
            self._update_display()

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
