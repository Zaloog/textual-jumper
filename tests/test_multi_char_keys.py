"""Tests for multi-character key functionality."""

from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_jumper.jump_overlay import JumpOverlay
from textual_jumper.jumper import Jumper


class TestMultiCharKeyGeneration:
    """Tests for multi-character key generation."""

    def test_single_char_keys_for_few_widgets(self):
        """Test that single-char keys are used when there are few widgets."""
        jumper = Jumper(keys=["a", "s", "d", "w"])
        keys = jumper._generate_available_keys(4)

        # Should return all single-char keys
        assert keys == ["a", "s", "d", "w"]
        assert all(len(k) == 1 for k in keys)

    def test_multi_char_keys_for_many_widgets(self):
        """Test that multi-char keys are generated when needed."""
        jumper = Jumper(keys=["a", "s", "d", "w"])
        keys = jumper._generate_available_keys(10)

        # Should have mix of single and multi-char keys
        assert len(keys) == 10
        single_char = [k for k in keys if len(k) == 1]
        multi_char = [k for k in keys if len(k) > 1]

        # Should have some single-char (half of base keys)
        assert len(single_char) == 2  # half of 4

        # Remaining should be multi-char
        assert len(multi_char) == 8

    def test_no_conflicts_between_single_and_multi(self):
        """Test that single-char keys don't conflict with multi-char prefixes."""
        jumper = Jumper(keys=["a", "s", "d", "w"])
        keys = jumper._generate_available_keys(10)

        single_char = [k for k in keys if len(k) == 1]
        multi_char = [k for k in keys if len(k) > 1]

        # No multi-char key should start with a single-char key
        for single in single_char:
            for multi in multi_char:
                assert not multi.startswith(single), f"Conflict: {multi} starts with {single}"

    def test_multi_char_key_format(self):
        """Test that multi-char keys use valid characters."""
        jumper = Jumper(keys=["a", "s", "d"])
        keys = jumper._generate_available_keys(10)

        # All multi-char keys should only use base characters
        for key in keys:
            for char in key:
                assert char in ["a", "s", "d"]

    def test_large_number_of_widgets(self):
        """Test key generation for a large number of widgets."""
        jumper = Jumper(keys=["a", "s", "d", "w", "h", "j", "k", "l"])
        keys = jumper._generate_available_keys(50)

        # Should generate enough keys
        assert len(keys) == 50

        # All keys should be unique
        assert len(set(keys)) == 50

    def test_triple_char_keys_when_needed(self):
        """Test that triple-char keys are generated when double-char aren't enough."""
        jumper = Jumper(keys=["a", "s"])
        # Need more than 2 single + (1 prefix * 2 suffixes) = 4 keys
        keys = jumper._generate_available_keys(10)

        # Should have some triple-char keys
        triple_char = [k for k in keys if len(k) == 3]
        assert len(triple_char) > 0


class TestMultiCharKeyAllocation:
    """Tests for multi-character key allocation in get_overlays."""

    async def test_allocation_with_many_widgets(self):
        """Test key allocation when there are many jumpable widgets."""

        class ManyWidgetsApp(App):
            def __init__(self, *args, **kwargs):
                self.jumper = Jumper(keys=["a", "s", "d"])
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.jumper
                # Create 10 inputs
                for i in range(10):
                    yield Input(id=f"input{i}")

        app = ManyWidgetsApp()
        async with app.run_test() as pilot:
            # Set all as jumpable
            for widget in pilot.app.query(Input).results():
                widget.jumpable = True  # type: ignore

            overlays = pilot.app.jumper.overlays

            # Should have 10 overlays
            assert len(overlays) == 10

            # Check key assignments
            keys = [info.key for info in overlays.values()]
            single_char = [k for k in keys if len(k) == 1]
            multi_char = [k for k in keys if len(k) > 1]

            # Should have single-char keys
            assert len(single_char) > 0
            # Should have multi-char keys
            assert len(multi_char) > 0

            # No conflicts
            for single in single_char:
                for multi in multi_char:
                    assert not multi.startswith(single)

    async def test_custom_keys_preserved_with_multi_char(self):
        """Test that custom key mappings are preserved when using multi-char keys."""

        class CustomKeyApp(App):
            def __init__(self, *args, **kwargs):
                self.jumper = Jumper(ids_to_keys={"input0": "z"}, keys=["a", "s"])
                super().__init__(*args, **kwargs)

            def compose(self) -> ComposeResult:
                yield self.jumper
                for i in range(5):
                    yield Input(id=f"input{i}")

        app = CustomKeyApp()
        async with app.run_test() as pilot:
            for widget in pilot.app.query(Input).results():
                widget.jumpable = True  # type: ignore

            overlays = pilot.app.jumper.overlays
            keys_by_id = {info.widget: info.key for info in overlays.values()}

            # Custom key should be preserved
            assert keys_by_id["input0"] == "z"

            # Other keys should be auto-generated
            auto_keys = [k for widget_id, k in keys_by_id.items() if widget_id != "input0"]
            assert len(auto_keys) == 4


class TestMultiCharJumpOverlay:
    """Tests for multi-character key input in JumpOverlay."""

    async def test_input_buffer_builds_up(self):
        """Test that input buffer accumulates characters."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")

            def on_mount(self):
                from textual.geometry import Offset

                from textual_jumper.jumper import JumpInfo

                overlays = {Offset(0, 0): JumpInfo("as", "widget1")}
                self.push_screen(JumpOverlay(overlays), self.set_focus)

        app = TestApp()
        async with app.run_test() as pilot:
            overlay = pilot.app.screen
            assert isinstance(overlay, JumpOverlay)

            # Initially buffer should be empty
            assert overlay._input_buffer == ""

            # Press 'a'
            await pilot.press("a")
            await pilot.pause()

            # Buffer should have 'a', screen should still be visible
            assert isinstance(pilot.app.screen, JumpOverlay)
            assert pilot.app.screen._input_buffer == "a"

            # Press 's'
            await pilot.press("s")
            await pilot.pause()

            # Should have jumped and dismissed
            assert not isinstance(pilot.app.screen, JumpOverlay)
            assert pilot.app.focused.id == "widget1"

    async def test_no_jump_on_partial_match(self):
        """Test that partial matches don't trigger jump."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")
                yield Input(id="widget2")

            def on_mount(self):
                from textual.geometry import Offset

                from textual_jumper.jumper import JumpInfo

                overlays = {
                    Offset(0, 0): JumpInfo("aa", "widget1"),
                    Offset(10, 10): JumpInfo("as", "widget2"),
                }
                self.push_screen(JumpOverlay(overlays), self.set_focus)

        app = TestApp()
        async with app.run_test() as pilot:
            # Press 'a' - should not jump yet
            await pilot.press("a")
            await pilot.pause()

            # Should still be on overlay
            assert isinstance(pilot.app.screen, JumpOverlay)
            assert pilot.app.screen._input_buffer == "a"

    async def test_invalid_sequence_clears_buffer(self):
        """Test that invalid key sequence clears the buffer."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")

            def on_mount(self):
                from textual.geometry import Offset

                from textual_jumper.jumper import JumpInfo

                overlays = {Offset(0, 0): JumpInfo("as", "widget1")}
                self.push_screen(JumpOverlay(overlays), self.set_focus)

        app = TestApp()
        async with app.run_test() as pilot:
            # Press 'a' then 'd' (invalid sequence)
            await pilot.press("a")
            await pilot.pause()
            await pilot.press("d")
            await pilot.pause()

            # Buffer should be cleared
            assert pilot.app.screen._input_buffer == ""

            # Should still be on overlay
            assert isinstance(pilot.app.screen, JumpOverlay)

    async def test_label_visibility_with_multi_char(self):
        """Test that labels are hidden/shown based on input buffer."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield Input(id="widget1")
                yield Input(id="widget2")

            def on_mount(self):
                from textual.geometry import Offset

                from textual_jumper.jumper import JumpInfo

                overlays = {
                    Offset(0, 0): JumpInfo("aa", "widget1"),
                    Offset(10, 10): JumpInfo("sd", "widget2"),
                }
                self.push_screen(JumpOverlay(overlays))

        app = TestApp()
        async with app.run_test() as pilot:
            from textual_jumper.jump_overlay import LetterLabel

            # Initially all labels should be visible
            labels = pilot.app.screen.query(LetterLabel)
            assert all(label.display for label in labels)

            # Press 'a'
            await pilot.press("a")
            await pilot.pause()

            # Only 'aa' label should be visible
            labels = pilot.app.screen.query(LetterLabel)
            visible_labels = [str(label.render()) for label in labels if label.display]
            assert "aa" in visible_labels
            assert "sd" not in [str(label.render()) for label in labels if label.display]
