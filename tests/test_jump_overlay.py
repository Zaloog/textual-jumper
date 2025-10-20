"""Tests for JumpOverlay and LetterLabel widgets."""

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Input

from textual_jumper.jump_overlay import JumpOverlay, LetterLabel
from textual_jumper.jumper import JumpInfo


class TestLetterLabel:
    """Tests for LetterLabel widget."""

    def test_letter_label_initialization(self):
        """Test LetterLabel can be initialized with text."""
        label = LetterLabel("a")
        assert str(label.render()) == "a"

    def test_letter_label_has_default_css(self):
        """Test LetterLabel has default CSS styling."""
        # Check that DEFAULT_CSS is defined
        assert hasattr(LetterLabel, "DEFAULT_CSS")
        assert "LetterLabel" in LetterLabel.DEFAULT_CSS
        assert "background:$warning" in LetterLabel.DEFAULT_CSS
        assert "color:black" in LetterLabel.DEFAULT_CSS

    async def test_letter_label_renders(self):
        """Test LetterLabel renders in an app."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield LetterLabel("x")

        app = TestApp()
        async with app.run_test() as pilot:
            label = pilot.app.query_one(LetterLabel)
            assert str(label.render()) == "x"

    async def test_letter_label_offset(self):
        """Test LetterLabel can have offset set."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                label = LetterLabel("a")
                label.offset = Offset(5, 10)
                yield label

        app = TestApp()
        async with app.run_test() as pilot:
            label = pilot.app.query_one(LetterLabel)
            assert label.offset == Offset(5, 10)


class TestJumpOverlay:
    """Tests for JumpOverlay modal screen."""

    def test_jump_overlay_initialization(self):
        """Test JumpOverlay initializes with overlays dict."""
        overlays = {
            Offset(0, 0): JumpInfo("a", "widget1", "focus"),
            Offset(10, 5): JumpInfo("s", "widget2", "focus"),
        }
        screen = JumpOverlay(overlays)
        assert screen.overlays == overlays

    def test_jump_overlay_empty_overlays(self):
        """Test JumpOverlay with empty overlays dict."""
        screen = JumpOverlay({})
        assert screen.overlays == {}

    async def test_jump_overlay_compose_creates_labels(self):
        """Test JumpOverlay compose yields LetterLabel for each overlay."""
        overlays = {
            Offset(0, 0): JumpInfo("a", "widget1", "focus"),
            Offset(10, 5): JumpInfo("s", "widget2", "focus"),
            Offset(20, 15): JumpInfo("d", "widget3", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input()

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()  # Wait for screen to fully mount
            # Should have 3 LetterLabels created
            labels = pilot.app.screen.query(LetterLabel)
            assert len(labels) == 3

            # Check that labels have correct text
            label_texts = {str(label.render()) for label in labels}
            assert label_texts == {"a", "s", "d"}

    async def test_jump_overlay_labels_have_correct_offsets(self):
        """Test LetterLabels in JumpOverlay have correct offsets."""
        overlays = {
            Offset(5, 10): JumpInfo("a", "widget1", "focus"),
            Offset(15, 20): JumpInfo("s", "widget2", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input()

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()  # Wait for screen to fully mount
            labels = pilot.app.screen.query(LetterLabel)
            assert len(labels) == 2

            # Check offsets
            offsets = {label.offset for label in labels}
            assert Offset(5, 10) in offsets
            assert Offset(15, 20) in offsets

    async def test_jump_overlay_has_escape_binding(self):
        """Test JumpOverlay has escape key binding."""
        overlays = {Offset(0, 0): JumpInfo("a", "widget1", "focus")}

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input()

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            overlay_screen = pilot.app.screen

            # Check bindings
            bindings = overlay_screen.BINDINGS
            assert len(bindings) > 0

            # Find escape binding
            escape_binding = None
            for binding in bindings:
                if binding.key == "escape":
                    escape_binding = binding
                    break

            assert escape_binding is not None
            assert escape_binding.action == "app.pop_screen"

    async def test_jump_overlay_escape_closes_screen(self):
        """Test pressing escape closes the JumpOverlay screen."""
        overlays = {Offset(0, 0): JumpInfo("a", "widget1", "focus")}

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input()

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            # Should be on overlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Press escape
            await pilot.press("escape")

            # Should be back to main screen
            assert not isinstance(pilot.app.screen, JumpOverlay)

    async def test_jump_overlay_is_modal(self):
        """Test JumpOverlay is a ModalScreen."""
        from textual.screen import ModalScreen

        overlays = {Offset(0, 0): JumpInfo("a", "widget1", "focus")}

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input()

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            # Check that JumpOverlay is a ModalScreen
            assert isinstance(pilot.app.screen, ModalScreen)

    async def test_jump_overlay_with_widget_references(self):
        """Test JumpOverlay works with direct widget references."""
        widget = Input()
        overlays = {
            Offset(0, 0): JumpInfo("a", widget, "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input()

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()  # Wait for screen to fully mount
            labels = pilot.app.screen.query(LetterLabel)
            assert len(labels) == 1
            assert str(labels[0].render()) == "a"

    async def test_jump_overlay_multiple_keys(self):
        """Test JumpOverlay with multiple different keys."""
        overlays = {
            Offset(0, 0): JumpInfo("q", "widget1", "focus"),
            Offset(10, 10): JumpInfo("w", "widget2", "focus"),
            Offset(20, 20): JumpInfo("e", "widget3", "focus"),
            Offset(30, 30): JumpInfo("r", "widget4", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input()

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()  # Wait for screen to fully mount
            labels = pilot.app.screen.query(LetterLabel)
            assert len(labels) == 4

            # Check all keys are present
            label_texts = {str(label.render()) for label in labels}
            assert label_texts == {"q", "w", "e", "r"}

    async def test_jump_overlay_key_press_jumps_to_widget(self):
        """Test pressing a jump key focuses the corresponding widget."""
        overlays = {
            Offset(0, 0): JumpInfo("a", "widget1", "focus"),
            Offset(10, 10): JumpInfo("s", "widget2", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")
                yield Input(id="widget2")

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays), self.set_focus)

        app = TestApp()
        async with app.run_test() as pilot:
            # Should be on overlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Press the jump key
            await pilot.press("a")
            await pilot.pause()

            # Should have dismissed and focused widget1
            assert not isinstance(pilot.app.screen, JumpOverlay)
            assert pilot.app.focused.id == "widget1"

    async def test_jump_overlay_invalid_key_does_nothing(self):
        """Test pressing an invalid key doesn't dismiss the overlay."""
        overlays = {
            Offset(0, 0): JumpInfo("a", "widget1", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            # Should be on overlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Press an invalid key
            await pilot.press("x")
            await pilot.pause()

            # Should still be on overlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

    async def test_jump_overlay_key_press_with_direct_widget_reference(self):
        """Test jumping with direct widget reference instead of ID."""

        class TestApp(App):
            def __init__(self, *args, **kwargs):
                self.input_widget = Input()
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.input_widget

            def on_mount(self):
                overlays = {
                    Offset(0, 0): JumpInfo("a", self.input_widget, "focus"),
                }
                self.push_screen(JumpOverlay(overlays), self.set_focus)

        app = TestApp()
        async with app.run_test() as pilot:
            # Press the jump key
            await pilot.press("a")
            await pilot.pause()

            # Should have dismissed and focused the widget
            assert not isinstance(pilot.app.screen, JumpOverlay)
            assert pilot.app.focused == pilot.app.input_widget

    async def test_jump_overlay_multiple_keys_correct_widget(self):
        """Test that pressing different keys jumps to correct widgets."""
        overlays = {
            Offset(0, 0): JumpInfo("a", "first", "focus"),
            Offset(10, 10): JumpInfo("s", "second", "focus"),
            Offset(20, 20): JumpInfo("d", "third", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="first")
                yield Input(id="second")
                yield Input(id="third")

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays), self.set_focus)

        app = TestApp()
        async with app.run_test() as pilot:
            # Press key for second widget
            await pilot.press("s")
            await pilot.pause()

            # Should focus the second widget
            assert pilot.app.focused.id == "second"

    async def test_jump_overlay_non_character_key_ignored(self):
        """Test that non-character keys (like arrows, F-keys) are ignored."""
        overlays = {
            Offset(0, 0): JumpInfo("a", "widget1", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            overlay = pilot.app.screen
            assert isinstance(overlay, JumpOverlay)

            # Press a non-character key (arrow key)
            await pilot.press("up")
            await pilot.pause()

            # Buffer should remain empty
            assert overlay.input_buffer == ""

            # Should still be on overlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

    async def test_jump_overlay_widget_not_found(self):
        """Test that jumping to a non-existent widget ID dismisses overlay gracefully."""
        overlays = {
            Offset(0, 0): JumpInfo("a", "nonexistent_widget", "focus"),
        }

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")

            def on_mount(self):
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            # Should be on overlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Press the jump key for non-existent widget
            await pilot.press("a")
            await pilot.pause()

            # Should have dismissed the overlay (graceful handling)
            assert not isinstance(pilot.app.screen, JumpOverlay)

    async def test_jump_overlay_click_mode_button(self):
        """Test that click mode simulates a click on a button."""
        from textual.widgets import Button

        class TestApp(App):
            def __init__(self, *args, **kwargs):
                self.button_clicked = False
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield Button("Test Button", id="test_btn")

            def on_button_pressed(self):
                self.button_clicked = True

            def on_mount(self):
                overlays = {
                    Offset(0, 0): JumpInfo("a", "test_btn", "click"),
                }
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            # Should be on overlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Press the jump key
            await pilot.press("a")
            await pilot.pause()

            # Should have dismissed overlay
            assert not isinstance(pilot.app.screen, JumpOverlay)

            # Button should have been clicked
            assert pilot.app.button_clicked

    async def test_jump_overlay_click_mode_with_direct_widget_reference(self):
        """Test that click mode works with direct widget reference."""
        from textual.widgets import Button

        class TestApp(App):
            def __init__(self, *args, **kwargs):
                self.button_clicked = False
                self.test_button = Button("Test Button")
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.test_button

            def on_button_pressed(self):
                self.button_clicked = True

            def on_mount(self):
                overlays = {
                    Offset(0, 0): JumpInfo("a", self.test_button, "click"),
                }
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            # Press the jump key
            await pilot.press("a")
            await pilot.pause()

            # Should have dismissed overlay
            assert not isinstance(pilot.app.screen, JumpOverlay)

            # Button should have been clicked
            assert pilot.app.button_clicked
