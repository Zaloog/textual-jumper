from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from textual_jumper.jumper import JumpInfo

from textual.binding import Binding
from textual.geometry import Offset
from textual.screen import ModalScreen
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
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close")
    ]
    def __init__(self, overlays: dict[Offset, "JumpInfo"]):
        self.overlays = overlays
        super().__init__()

    def compose(self):
        for offset, jump_info in self.overlays.items():
            label = LetterLabel(jump_info.key)
            label.offset = offset
            yield label


    def on_mount(self):
        self.notify(f"{self.overlays}", markup=False)

