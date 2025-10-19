# Textual Jumper

A keyboard-driven navigation widget for Textual TUI applications. Jump to any focusable widget instantly using intuitive keyboard shortcuts!

## Features

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
from textual.widgets import Input, Header, Footer
from textual_jumper import Jumper

class MyApp(App):
    BINDINGS = [("ctrl+o", "show_overlay", "Jump")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Jumper()

        name_input = Input(placeholder="Name")
        name_input.jumpable = True
        yield name_input

        email_input = Input(placeholder="Email")
        email_input.jumpable = True
        yield email_input

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

## Requirements

- Python 3.10+
- Textual 6.3.0+

## Development

```bash
# Clone repository
git clone https://github.com/zaloog/textual-jumper.git
cd textual-jumper

# Install with dev dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run linting
uv run pre-commit run --all-files
```

## Publishing

The package is automatically published to PyPI when a new release is created on GitHub:

1. Update version in `pyproject.toml`
2. Create a new tag: `git tag v0.1.0 && git push origin v0.1.0`
3. Create a GitHub release from the tag
4. The publish workflow will automatically build and upload to PyPI

Note: PyPI publishing uses [Trusted Publishers](https://docs.pypi.org/trusted-publishers/) (no API token needed). Configure this in your PyPI project settings before the first release.

## License

MIT License

## Acknowledgments

Inspired by Vim's EasyMotion plugin.
Built with Textual by Textualize.io.
Created with Claude Code.
