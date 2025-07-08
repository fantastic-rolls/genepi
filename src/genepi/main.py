import importlib.metadata

from art import text2art
from textual.app import App, ComposeResult
from textual.containers import Center, HorizontalGroup, VerticalGroup
from textual.screen import Screen
from textual.widgets import Button, Static

from genepi.components.pre_render_view import PreRenderScreen
from genepi.components.prepare_view import PrepareScreen
from genepi.components.Widgets.directory_picker import FilePicker
from genepi.models.episode import Episode


class Hub(Screen):
    DEFAULT_CSS = """
    Screen {
        align: center middle;
    }

    Static {
        width: auto;
    }

    #title {
        width: auto;
        height: 20;
        margin-top: 5;
        color: $text-primary;
    }

    #hub {
        width: auto;
    }
    #hub Button{
        width: 33.3%;
        height: 5;
        margin: 2;
    }

    #header {
        align: center middle;
        width: auto;
        text-align: center;
    }

    #menu {
        margin-top: 5;
        width: auto;
        padding: 0 10;
    }

    #footer {
        dock: bottom;
        padding: 1;
    }
    """

    def __init__(self, name=None, id=None, classes=None) -> None:
        super().__init__(name, id, classes)
        self._episode_file: str | None = None

    def compose(self) -> ComposeResult:
        version = importlib.metadata.version("genepi")

        with VerticalGroup(id="header"):
            yield Center(Static(text2art("GENEPI", font="amcaaa01"), id="title"))
            yield Center(
                Static(
                    "[bold $primary]Gen[/]erate [bold $primary]epi[/]sodes for"
                    "Fantastic-Rolls podcast."
                )
            )

        yield VerticalGroup(
            Center(
                FilePicker(
                    filters={"Episode": [".json"]},
                    placeholder="Load episode definition (.json)",
                    callback=self.handle_file_picked,
                )
            ),
            Center(
                HorizontalGroup(
                    Button("Prepare", id="prepare", variant="primary"),
                    Button(
                        "Pre Render\n-\n[italic](After Effects)[/]",
                        id="pre-render",
                        variant="primary",
                        disabled=True,
                    ),
                    Button(
                        "Render\n-\n[italic](Premiere)[/]",
                        id="render",
                        variant="primary",
                        disabled=True,
                    ),
                ),
                id="hub",
            ),
            Center(Button("Quit", id="quit", variant="error")),
            id="menu",
        )
        with Center(id="footer"):
            yield Static(
                f"Genepi - version {version} - Coded with 💜 for Fantastic Rolls"
            )

    def handle_file_picked(self, file: str) -> None:
        btn_generate = self.query_exactly_one("#pre-render", Button)
        btn_generate.disabled = not file
        self._episode_file = file
        Episode().load_file(file)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        elif event.button.id == "prepare":
            self.app.push_screen(PrepareScreen())

        elif event.button.id == "pre-render":
            self.app.push_screen(PreRenderScreen(self._episode_file))


class Genepi(App):
    CSS_PATH = "genepi.tcss"

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def on_ready(self) -> None:
        self.push_screen(Hub())


def main() -> None:
    app = Genepi()
    app.run()


if __name__ == "__main__":
    main()
