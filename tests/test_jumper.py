"""Tests for the Jumper widget."""

import pytest
from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Button, Input, Label

from textual_jumper.jumper import DEFAULT_KEYS, Jumper, JumpInfo


class MockApp(App):
    """Mock app for testing Jumper."""

    def __init__(self, *args, **kwargs):
        self.jumper = Jumper()
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield self.jumper
        yield Input(id="input1")
        yield Input(id="input2")
        yield Button("Submit", id="button1")
        yield Label("Not focusable")


class TestJumperInitialization:
    """Tests for Jumper initialization."""

    def test_default_initialization(self):
        """Test Jumper initializes with default values."""
        jumper = Jumper()
        assert jumper.ids_to_keys == {}
        assert jumper.keys == DEFAULT_KEYS
        assert jumper._overlays == {}
        assert jumper.display is False

    def test_custom_ids_to_keys(self):
        """Test Jumper with custom ids_to_keys mapping."""
        custom_mapping = {"input1": "x", "input2": "y"}
        jumper = Jumper(ids_to_keys=custom_mapping)
        assert jumper.ids_to_keys == custom_mapping

    def test_custom_keys(self):
        """Test Jumper with custom available keys."""
        custom_keys = ["1", "2", "3", "4"]
        jumper = Jumper(keys=custom_keys)
        assert jumper.keys == custom_keys

    def test_both_custom_parameters(self):
        """Test Jumper with both custom mappings and keys."""
        custom_mapping = {"input1": "x"}
        custom_keys = ["q", "w", "e"]
        jumper = Jumper(ids_to_keys=custom_mapping, keys=custom_keys)
        assert jumper.ids_to_keys == custom_mapping
        assert jumper.keys == custom_keys


class TestGetFreeKey:
    """Tests for _get_free_key method."""

    def test_get_free_key_empty_overlays(self):
        """Test getting free key when no keys are in use."""
        jumper = Jumper()
        jumper._overlays = {}
        free_key = jumper._get_free_key()
        assert free_key == "a"  # First key in DEFAULT_KEYS

    def test_get_free_key_some_used(self):
        """Test getting free key when some keys are in use."""
        jumper = Jumper()
        jumper._overlays = {
            Offset(0, 0): JumpInfo("a", "widget1"),
            Offset(1, 1): JumpInfo("s", "widget2"),
        }
        free_key = jumper._get_free_key()
        assert free_key == "d"  # Next available key

    def test_get_free_key_all_used(self):
        """Test getting free key when all keys are exhausted."""
        jumper = Jumper(keys=["a", "b"])
        jumper._overlays = {
            Offset(0, 0): JumpInfo("a", "widget1"),
            Offset(1, 1): JumpInfo("b", "widget2"),
        }
        free_key = jumper._get_free_key()
        assert free_key is None

    def test_get_free_key_custom_keys(self):
        """Test getting free key with custom key list."""
        custom_keys = ["x", "y", "z"]
        jumper = Jumper(keys=custom_keys)
        jumper._overlays = {Offset(0, 0): JumpInfo("x", "widget1")}
        free_key = jumper._get_free_key()
        assert free_key == "y"


class TestGetOverlays:
    """Tests for get_overlays method."""

    async def test_get_overlays_with_jumpable_widgets(self):
        """Test get_overlays finds jumpable widgets."""
        app = MockApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper

            # Set jumpable attribute on focusable widgets
            input1 = pilot.app.query_one("#input1", Input)
            input2 = pilot.app.query_one("#input2", Input)
            button = pilot.app.query_one("#button1", Button)

            input1.jumpable = True
            input2.jumpable = True
            button.jumpable = True

            # Get overlays
            jumper.get_overlays()

            # Should have 3 overlays (input1, input2, button)
            assert len(jumper._overlays) == 3

            # Check that all widgets are mapped
            widget_ids = [info.widget for info in jumper._overlays.values()]
            assert "input1" in widget_ids
            assert "input2" in widget_ids
            assert "button1" in widget_ids

    async def test_get_overlays_without_jumpable_attribute(self):
        """Test get_overlays ignores widgets without jumpable attribute."""
        app = MockApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper

            # Don't set jumpable attribute
            jumper.get_overlays()

            # Should have 0 overlays (no widgets have jumpable=True)
            assert len(jumper._overlays) == 0

    async def test_get_overlays_with_custom_keys(self):
        """Test get_overlays uses custom key mapping."""
        custom_mapping = {"input1": "x", "button1": "z"}

        class CustomKeyApp(App):
            def compose(self) -> ComposeResult:
                self.jumper = Jumper(ids_to_keys=custom_mapping)
                yield self.jumper
                yield Input(id="input1")
                yield Input(id="input2")
                yield Button("Submit", id="button1")

        app = CustomKeyApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper

            # Set jumpable attribute
            for widget in [
                pilot.app.query_one("#input1"),
                pilot.app.query_one("#input2"),
                pilot.app.query_one("#button1"),
            ]:
                widget.jumpable = True

            jumper.get_overlays()

            # Find the JumpInfo for each widget
            infos = list(jumper._overlays.values())
            keys_by_id = {info.widget: info.key for info in infos}

            # Check custom mappings are used
            assert keys_by_id["input1"] == "x"
            assert keys_by_id["button1"] == "z"
            # input2 should get an auto-assigned key
            assert keys_by_id["input2"] in DEFAULT_KEYS

    async def test_get_overlays_non_focusable_ignored(self):
        """Test get_overlays ignores non-focusable widgets."""
        app = MockApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper

            # Set jumpable on all widgets including Label
            label = pilot.app.query_one(Label)
            label.jumpable = True

            jumper.get_overlays()

            # Label is not focusable, so should not be in overlays
            # Only 0 widgets should be there (Inputs and Button don't have jumpable=True yet)
            assert len(jumper._overlays) == 0

    async def test_overlays_property(self):
        """Test overlays property calls get_overlays and returns result."""
        app = MockApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper

            # Set jumpable attribute
            input1 = pilot.app.query_one("#input1", Input)
            input1.jumpable = True

            overlays = jumper.overlays

            # Should have called get_overlays and returned the dict
            assert isinstance(overlays, dict)
            assert len(overlays) == 1

    async def test_get_overlays_widget_without_id(self):
        """Test get_overlays handles widgets without IDs."""

        class NoIdApp(App):
            def compose(self) -> ComposeResult:
                self.jumper = Jumper()
                yield self.jumper
                # Widget without an ID
                self.no_id_input = Input()
                yield self.no_id_input

        app = NoIdApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper
            pilot.app.no_id_input.jumpable = True

            jumper.get_overlays()

            # Should have 1 overlay with direct widget reference
            assert len(jumper._overlays) == 1
            info = list(jumper._overlays.values())[0]
            # Widget reference should be the widget itself, not an ID
            assert info.widget == pilot.app.no_id_input


class TestJumperMethods:
    """Tests for other Jumper methods."""

    async def test_focus_returned_widget(self):
        """Test focus_returned_widget sets focus correctly."""
        app = MockApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper
            input1 = pilot.app.query_one("#input1", Input)

            jumper.focus_returned_widget(input1)

            # Check that focus was set to input1
            assert pilot.app.focused == input1

    async def test_show_pushes_screen(self):
        """Test show method pushes JumpOverlay screen."""
        app = MockApp()
        async with app.run_test() as pilot:
            jumper = pilot.app.jumper

            # Set up some jumpable widgets
            input1 = pilot.app.query_one("#input1", Input)
            input1.jumpable = True

            # Mock screen stack length
            initial_screen_count = len(pilot.app.screen_stack)

            jumper.show()
            await pilot.pause()

            # Should have pushed a new screen
            assert len(pilot.app.screen_stack) > initial_screen_count


class TestJumpInfo:
    """Tests for JumpInfo NamedTuple."""

    def test_jump_info_with_id(self):
        """Test JumpInfo with widget ID."""
        info = JumpInfo("a", "widget1")
        assert info.key == "a"
        assert info.widget == "widget1"

    def test_jump_info_with_widget_reference(self):
        """Test JumpInfo with direct widget reference."""
        widget = Input()
        info = JumpInfo("b", widget)
        assert info.key == "b"
        assert info.widget == widget

    def test_jump_info_immutability(self):
        """Test JumpInfo is immutable (NamedTuple property)."""
        info = JumpInfo("a", "widget1")
        with pytest.raises(AttributeError):
            info.key = "b"
