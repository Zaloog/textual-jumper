from typing import Any, NamedTuple

from textual.errors import NoWidget
from textual.geometry import Offset
from textual.widget import Widget

from textual_jumper.jump_overlay import JumpOverlay


class JumpInfo(NamedTuple):
    """Information returned by the jumper for each jump target."""

    key: str
    """The key which should trigger the jump."""

    widget: str | Widget
    """Either the ID or a direct reference to the widget."""


DEFAULT_KEYS = ["a", "s", "d", "w", "h", "j", "k", "l"]


class Jumper(Widget):
    def __init__(
        self,
        ids_to_keys: dict[str, str] | None = None,
        keys: list[str] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.ids_to_keys = ids_to_keys or {}
        self._overlays: dict[Offset, JumpInfo] = {}
        self.keys = keys or DEFAULT_KEYS
        super().__init__(*args, **kwargs)
        self.display = False

    def _get_free_key(self) -> str | None:
        keys_in_use = [jump_info.key for jump_info in self._overlays.values()]
        for key in self.keys:
            if key not in keys_in_use:
                return key
        return None

    def get_overlays(self) -> dict[Offset, JumpInfo]:
        """Return a dictionary of all the jump targets"""
        screen = self.screen
        children: list[Widget] = screen.walk_children(Widget)
        self._overlays = {}
        ids_to_keys = self.ids_to_keys
        for child in children:
            try:
                widget_x, widget_y = screen.get_offset(child)
            except NoWidget:
                # The widget might not be visible in the layout
                # due to it being hidden in some modes.
                continue

            has_attribute_and_jumpable = getattr(child, "jumpable", False)
            can_focus = child.can_focus
            if not all((can_focus, has_attribute_and_jumpable)):
                continue

            widget_offset = Offset(widget_x, widget_y)
            if child.id and child.id in ids_to_keys:
                self._overlays[widget_offset] = JumpInfo(
                    ids_to_keys[child.id],
                    child.id,
                )
            else:
                free_key = self._get_free_key()
                if free_key is not None:
                    self._overlays[widget_offset] = JumpInfo(
                        free_key,
                        child.id or child,
                    )
        return self._overlays

    def focus_returned_widget(self, widget: Widget) -> None:
        self.app.set_focus(widget)

    def show(self) -> None:
        self.app.push_screen(JumpOverlay(self.overlays), self.app.set_focus)

    @property
    def overlays(self) -> dict[Offset, JumpInfo]:
        self.get_overlays()
        return self._overlays
