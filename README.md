<!-- Icons -->
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI-Server](https://img.shields.io/pypi/v/textual-jumper.svg)](https://pypi.org/project/textual-jumper/)
[![Pyversions](https://img.shields.io/pypi/pyversions/textual-jumper.svg)](https://pypi.python.org/pypi/textual-jumper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/textual-jumper)](https://pepy.tech/project/textual-jumper)
[![Coverage Status](https://coveralls.io/repos/github/Zaloog/textual-jumper/badge.svg?branch=main)](https://coveralls.io/github/Zaloog/textual-jumper?branch=main)

# Textual Jumper

A keyboard-driven navigation widget for Textual TUI applications. Jump to any focusable widget instantly using intuitive keyboard shortcuts!
> Note: This was created with Claude Code


## Features
![cover_image](https://raw.githubusercontent.com/Zaloog/textual-jumper/main/docs/images/cover_image.png)

- Instant Navigation - Jump to any widget with 1-2 keystrokes
- Multi-Character Keys - Automatically generates key combinations for many widgets
- Visual Feedback - Real-time highlighting shows typed characters
- Customizable - Define your own key mappings or use defaults
- Zero Dependencies - Only requires Textual
- Easy Integration - Add to existing apps in minutes

## Installation

Using uv:

```bash
uv add textual-jumper
```

Using pip:

```bash
pip install textual-jumper
```

## Try the Demo

Run the interactive demo to see Textual Jumper in action:

```bash
uvx textual-jumper
```

Press `Ctrl+O` to activate jump mode, then press a key to jump to that widget!

## Quick Start

```python
from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Header, Footer
from textual_jumper import Jumper

class MyApp(App):
    BINDINGS = [("ctrl+o", "show_overlay", "Jump")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Jumper()

        # Focus mode - widget will receive focus
        name_input = Input(placeholder="Name")
        name_input.jump_mode = "focus"
        yield name_input

        email_input = Input(placeholder="Email")
        email_input.jump_mode = "focus"
        yield email_input

        # Click mode - widget will be clicked
        submit_button = Button("Submit")
        submit_button.jump_mode = "click"
        yield submit_button

        yield Footer()

    def action_show_overlay(self) -> None:
        self.query_one(Jumper).show()

if __name__ == "__main__":
    MyApp().run()
```

## How It Works

### Single-Character Keys

For 8 or fewer widgets, each gets a single character:

```
Input Field 1  [a]
Input Field 2  [s]
Button         [d]
```

Press `a` to jump to Input Field 1.

### Multi-Character Keys

For 9+ widgets, the system generates combinations with no conflicts:

```
Input 1   [a]     Input 5   [ha]    Input 9   [js]
Input 2   [s]     Input 6   [hs]    Input 10  [jd]
Input 3   [d]     Input 7   [hd]    Input 11  [jw]
Input 4   [w]     Input 8   [ja]
```

Smart allocation strategy ensures no conflicts between single and multi-character keys.

## Jump Modes

textual-jumper supports two jump modes for different widget interactions:

### Focus Mode

Widgets with `jump_mode = "focus"` will receive focus when jumped to. This is ideal for input fields, text areas, and other widgets where you want to interact with them directly.

```python
name_input = Input(placeholder="Name")
name_input.jump_mode = "focus"
```

### Click Mode

Widgets with `jump_mode = "click"` will be clicked automatically when jumped to. This is perfect for Buttons, Selects, and other widgets that trigger actions.

```python
submit_button = Button("Submit")
submit_button.jump_mode = "click"
```

Also the Widget you want to jump to needs to be focusable, so `Widget.can_focus = True` must be set, if the widget is not focusable
by default.

## Configuration

### Custom Key Mappings

```python
jumper = Jumper(ids_to_keys={
    "username": "u",
    "password": "p",
    "submit": "s"
})
```

### Custom Available Keys

```python
jumper = Jumper(keys=["a", "s", "d", "f", "j", "k", "l", ";"])
```

## Acknowledgments

Inspired by Darren Burns jump functionality in [Posting].

## Feedback and Issues
Feel free to reach out and share your feedback, or open an [Issue],
if something doesn't work as expected.
Also check the [Changelog] for new updates.


<!-- Repo Links -->
[Changelog]: https://github.com/Zaloog/textual-jumper/blob/main/CHANGELOG.md
[Issue]: https://github.com/Zaloog/textual-jumper/issues

[Posting]: https://github.com/darrenburns/posting
