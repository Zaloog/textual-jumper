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

    def _generate_available_keys(self, num_needed: int) -> list[str]:
        """Generate enough keys for all widgets, using combinations if needed.

        Strategy:
        - If num_needed <= half of available keys: use single-char keys
        - Otherwise: use combinations, reserving some keys for single-char,
          and using the rest for 2-char combinations to avoid conflicts

        Args:
            num_needed: Number of unique keys needed

        Returns:
            List of available keys (single or multi-character)
        """
        base_keys = self.keys
        num_base = len(base_keys)

        # If we need fewer keys than available, just use single characters
        if num_needed <= num_base:
            return base_keys[:num_needed]

        # For many widgets, use a mix of single and double-character keys
        # Reserve half the keys for single-char, use rest for double-char prefixes
        single_char_count = num_base // 2

        available = []

        # Add single-character keys
        available.extend(base_keys[:single_char_count])

        # Add double-character keys using remaining keys as prefixes
        # This ensures no conflict: 'a' is single-char, 'ha', 'hs', etc. are double-char
        for prefix in base_keys[single_char_count:]:
            for suffix in base_keys:
                available.append(prefix + suffix)
                if len(available) >= num_needed:
                    return available

        # If still not enough, use triple-character combinations
        for prefix1 in base_keys[single_char_count:]:
            for prefix2 in base_keys:
                for suffix in base_keys:
                    available.append(prefix1 + prefix2 + suffix)
                    if len(available) >= num_needed:
                        return available

        return available

    def _get_free_key(self, available_keys: list[str]) -> str | None:
        """Get the next available key from the provided list.

        Args:
            available_keys: List of all available keys

        Returns:
            Next unused key or None if all exhausted
        """
        keys_in_use = [jump_info.key for jump_info in self._overlays.values()]
        for key in available_keys:
            if key not in keys_in_use:
                return key
        return None

    def get_overlays(self) -> dict[Offset, JumpInfo]:
        """Return a dictionary of all the jump targets"""
        screen = self.screen
        children: list[Widget] = screen.walk_children(Widget)
        self._overlays = {}
        ids_to_keys = self.ids_to_keys

        # First pass: collect all jumpable widgets and count those needing auto-keys
        jumpable_widgets: list[tuple[Offset, Widget]] = []
        custom_key_count = 0

        for child in children:
            try:
                widget_x, widget_y = screen.get_offset(child)
            except NoWidget:
                continue

            has_attribute_and_jumpable = getattr(child, "jumpable", False)
            can_focus = child.can_focus
            if not all((can_focus, has_attribute_and_jumpable)):
                continue

            widget_offset = Offset(widget_x, widget_y)
            jumpable_widgets.append((widget_offset, child))

            # Count widgets with custom keys
            if child.id and child.id in ids_to_keys:
                custom_key_count += 1

        # Calculate how many auto-generated keys we need
        auto_key_count = len(jumpable_widgets) - custom_key_count
        available_keys = self._generate_available_keys(auto_key_count)

        # Second pass: assign keys to widgets
        for widget_offset, child in jumpable_widgets:
            if child.id and child.id in ids_to_keys:
                # Use custom key mapping
                self._overlays[widget_offset] = JumpInfo(
                    ids_to_keys[child.id],
                    child.id,
                )
            else:
                # Use auto-generated key
                free_key = self._get_free_key(available_keys)
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
