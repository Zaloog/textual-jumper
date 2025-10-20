"""Integration tests for textual-jumper."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input

from textual_jumper.jump_overlay import JumpOverlay, LetterLabel
from textual_jumper.jumper import Jumper


class IntegrationTestApp(App):
    """App for integration testing."""

    BINDINGS = [("ctrl+o", "show_overlay", "Show Jump Overlay")]

    def __init__(self, *args, **kwargs):
        self.jumper = Jumper()
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.jumper
        with Vertical():
            yield Input(id="name", placeholder="Name")
            yield Input(id="email", placeholder="Email")
            with Horizontal():
                yield Input(id="phone", placeholder="Phone")
                yield Input(id="address", placeholder="Address")
            yield Button("Submit", id="submit_btn")
        yield Footer()

    def action_show_overlay(self):
        """Show the jump overlay."""
        self.jumper.show()


class TestIntegration:
    """Integration tests for the complete jump workflow."""

    async def test_complete_jump_workflow(self):
        """Test the complete workflow of showing overlay and jumping."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Set jump_mode on all inputs and buttons
            for widget in pilot.app.query(Input).results():
                widget.jump_mode = "focus"
            pilot.app.query_one("#submit_btn", Button).jump_mode = "focus"

            # Trigger the jump overlay
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Should be on the JumpOverlay screen
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Wait for labels to render
            await pilot.pause()

            # Should have 5 LetterLabels (4 inputs + 1 button)
            labels = pilot.app.screen.query(LetterLabel)
            assert len(labels) == 5

    async def test_overlay_shows_correct_keys(self):
        """Test that overlay shows correct keys for widgets."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Set jumpable
            for widget in pilot.app.query(Input).results():
                widget.jump_mode = "focus"

            # Get overlays
            overlays = pilot.app.jumper.overlays

            # Should have keys from DEFAULT_KEYS
            keys = [info.key for info in overlays.values()]
            assert len(keys) == 4
            assert all(key in ["a", "s", "d", "w", "h", "j", "k", "l"] for key in keys)

    async def test_custom_key_mapping_integration(self):
        """Test integration with custom key mappings."""

        class CustomApp(App):
            def __init__(self, *args, **kwargs):
                # Custom mapping: name->1, email->2, submit->3
                self.jumper = Jumper(ids_to_keys={"name": "1", "email": "2", "submit_btn": "3"})
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.jumper
                yield Input(id="name")
                yield Input(id="email")
                yield Button("Submit", id="submit_btn")

        app = CustomApp()
        async with app.run_test() as pilot:
            # Set jumpable
            pilot.app.query_one("#name").jump_mode = "focus"
            pilot.app.query_one("#email").jump_mode = "focus"
            pilot.app.query_one("#submit_btn").jump_mode = "focus"

            # Get overlays
            overlays = pilot.app.jumper.overlays
            keys_by_id = {info.widget: info.key for info in overlays.values()}

            # Check custom keys are used
            assert keys_by_id["name"] == "1"
            assert keys_by_id["email"] == "2"
            assert keys_by_id["submit_btn"] == "3"

    async def test_nested_widgets_detected(self):
        """Test that widgets in nested containers are detected."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Set jumpable on nested inputs
            for widget in pilot.app.query(Input).results():
                widget.jump_mode = "focus"

            overlays = pilot.app.jumper.overlays

            # Should find all 4 inputs including nested ones
            assert len(overlays) == 4

            # Check that nested widgets are included
            widget_ids = [info.widget for info in overlays.values()]
            assert "phone" in widget_ids
            assert "address" in widget_ids

    async def test_only_jumpable_widgets_shown(self):
        """Test that only widgets with jumpable=True are shown."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Only set jumpable on one widget
            pilot.app.query_one("#name").jump_mode = "focus"

            overlays = pilot.app.jumper.overlays

            # Should only have 1 overlay
            assert len(overlays) == 1
            info = list(overlays.values())[0]
            assert info.widget == "name"

    async def test_escape_closes_overlay(self):
        """Test that pressing escape closes the overlay."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Set jumpable
            pilot.app.query_one("#name").jump_mode = "focus"

            # Show overlay
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Should be on overlay
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Press escape
            await pilot.press("escape")
            await pilot.pause()

            # Should be back to main screen
            assert not isinstance(pilot.app.screen, JumpOverlay)

    async def test_jumper_display_is_false(self):
        """Test that jumper widget is not displayed."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper
            assert jumper.display is False

    async def test_overlay_regenerated_on_show(self):
        """Test that overlays are regenerated each time show() is called."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Initially, only one widget is jumpable
            pilot.app.query_one("#name").jump_mode = "focus"

            # Get overlays
            overlays1 = pilot.app.jumper.overlays
            assert len(overlays1) == 1

            # Make another widget jumpable
            pilot.app.query_one("#email").jump_mode = "focus"

            # Get overlays again
            overlays2 = pilot.app.jumper.overlays
            assert len(overlays2) == 2

    async def test_multiple_widgets_with_different_types(self):
        """Test jumping with different widget types (Input, Button)."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Set jumpable on different widget types
            pilot.app.query_one("#name", Input).jump_mode = "focus"
            pilot.app.query_one("#submit_btn", Button).jump_mode = "focus"

            overlays = pilot.app.jumper.overlays

            # Should have 2 overlays
            assert len(overlays) == 2

            # Check both widget types are present
            widget_ids = [info.widget for info in overlays.values()]
            assert "name" in widget_ids
            assert "submit_btn" in widget_ids

    async def test_widget_without_id_in_integration(self):
        """Test integration with widgets that don't have IDs."""

        class NoIdApp(App):
            def __init__(self, *args, **kwargs):
                self.jumper = Jumper()
                self.input_no_id = Input()
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.jumper
                yield Input(id="with_id")
                yield self.input_no_id

        app = NoIdApp()
        async with app.run_test() as pilot:
            # Set jumpable on both
            pilot.app.query_one("#with_id").jump_mode = "focus"
            pilot.app.input_no_id.jump_mode = "focus"

            overlays = pilot.app.jumper.overlays

            # Should have 2 overlays
            assert len(overlays) == 2

            # Check that one uses ID and one uses widget reference
            widgets = [info.widget for info in overlays.values()]
            assert "with_id" in widgets
            assert pilot.app.input_no_id in widgets

    async def test_key_exhaustion_handling(self):
        """Test behavior when single-char keys run out - should generate multi-char keys."""

        class ManyWidgetsApp(App):
            def __init__(self, *args, **kwargs):
                # Only 2 keys available
                self.jumper = Jumper(keys=["x", "y"])
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.jumper
                yield Input(id="input1")
                yield Input(id="input2")
                yield Input(id="input3")

        app = ManyWidgetsApp()
        async with app.run_test() as pilot:
            # Set jumpable on all 3 inputs
            for widget in pilot.app.query(Input).results():
                widget.jump_mode = "focus"

            overlays = pilot.app.jumper.overlays

            # All 3 should get keys (using multi-char keys when needed)
            assert len(overlays) == 3

            # All keys should be valid
            keys = [info.key for info in overlays.values()]
            assert all(key is not None for key in keys)

            # Should have mix of single and multi-char keys
            single_char = [k for k in keys if len(k) == 1]
            multi_char = [k for k in keys if len(k) > 1]

            # Should have 1 single-char (half of 2 keys)
            assert len(single_char) == 1
            # Should have 2 multi-char
            assert len(multi_char) == 2

    async def test_jump_to_widget_with_key_press(self):
        """Test complete jump workflow: show overlay and jump to widget."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Set jumpable
            pilot.app.query_one("#name").jump_mode = "focus"
            pilot.app.query_one("#email").jump_mode = "focus"
            pilot.app.query_one("#phone").jump_mode = "focus"

            # Show overlay
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Should be on overlay
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Get the key for the email field
            overlays = pilot.app.jumper.overlays
            email_key = None
            for info in overlays.values():
                if info.widget == "email":
                    email_key = info.key
                    break

            assert email_key is not None

            # Press that key
            await pilot.press(email_key)
            await pilot.pause()

            # Should have dismissed overlay and focused email
            assert not isinstance(pilot.app.screen, JumpOverlay)
            assert pilot.app.focused.id == "email"

    async def test_jump_cancellation_with_escape(self):
        """Test that escape cancels without jumping."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Set jumpable
            pilot.app.query_one("#name").jump_mode = "focus"

            # Focus name initially
            pilot.app.query_one("#name").focus()
            await pilot.pause()

            # Show overlay
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Should be on overlay
            assert isinstance(pilot.app.screen, JumpOverlay)

            # Press escape to cancel
            await pilot.press("escape")
            await pilot.pause()

            # Should have dismissed but still focused on name
            assert not isinstance(pilot.app.screen, JumpOverlay)
            # Focus should remain on the originally focused widget
            assert pilot.app.focused.id == "name"

    async def test_jump_with_button_widget(self):
        """Test jumping to a button widget."""
        app = IntegrationTestApp()
        async with app.run_test() as pilot:
            # Only make button jumpable
            pilot.app.query_one("#submit_btn").jump_mode = "focus"

            # Show overlay
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Get button's jump key
            overlays = pilot.app.jumper.overlays
            button_key = list(overlays.values())[0].key

            # Press that key
            await pilot.press(button_key)
            await pilot.pause()

            # Should focus the button
            assert pilot.app.focused.id == "submit_btn"

    async def test_jump_with_click_mode(self):
        """Test jumping to a widget with click mode."""

        class ClickModeApp(App):
            def __init__(self, *args, **kwargs):
                self.jumper = Jumper()
                self.button_clicked = False
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.jumper
                yield Button("Click Me", id="clickable_btn")

            def on_button_pressed(self):
                self.button_clicked = True

        app = ClickModeApp()
        async with app.run_test() as pilot:
            # Set jump_mode to click
            button = pilot.app.query_one("#clickable_btn", Button)
            button.jump_mode = "click"

            # Show overlay
            pilot.app.jumper.show()
            await pilot.pause()

            # Get the key for the button
            overlays = pilot.app.jumper.overlays
            button_key = list(overlays.values())[0].key

            # Press that key to jump and click
            await pilot.press(button_key)
            await pilot.pause()

            # Should have dismissed overlay
            assert not isinstance(pilot.app.screen, JumpOverlay)

            # Button should have been clicked
            assert pilot.app.button_clicked

    async def test_mixed_jump_modes(self):
        """Test that different widgets can have different jump modes."""

        class MixedModeApp(App):
            def __init__(self, *args, **kwargs):
                self.jumper = Jumper()
                self.button_clicked = False
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.jumper
                yield Input(id="focus_input")
                yield Button("Click Me", id="click_btn")

            def on_button_pressed(self):
                self.button_clicked = True

        app = MixedModeApp()
        async with app.run_test() as pilot:
            # Set different jump modes
            pilot.app.query_one("#focus_input").jump_mode = "focus"
            pilot.app.query_one("#click_btn").jump_mode = "click"

            # Show overlay
            pilot.app.jumper.show()
            await pilot.pause()

            # Get overlays
            overlays = pilot.app.jumper.overlays

            # Find keys for each widget
            input_key = None
            button_key = None
            for info in overlays.values():
                if info.widget == "focus_input":
                    input_key = info.key
                    assert info.jump_mode == "focus"
                elif info.widget == "click_btn":
                    button_key = info.key
                    assert info.jump_mode == "click"

            assert input_key is not None
            assert button_key is not None

            # Test focus mode first
            await pilot.press(input_key)
            await pilot.pause()

            # Should have focused the input
            assert pilot.app.focused.id == "focus_input"

            # Show overlay again
            pilot.app.jumper.show()
            await pilot.pause()

            # Test click mode
            await pilot.press(button_key)
            await pilot.pause()

            # Button should have been clicked
            assert pilot.app.button_clicked
