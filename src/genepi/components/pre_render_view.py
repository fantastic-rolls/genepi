from typing import Final

from textual.app import ComposeResult
from textual.containers import Center, HorizontalGroup
from textual.screen import Screen
from textual.widgets import Button, Static

from genepi.models.episode import Episode
from genepi.runner import generate_ae_script, run_script


class PreRenderScreen(Screen):
    BINDINGS: Final = [("escape", "app.pop_screen", "Pop screen")]
    RENDERING_FACTOR: Final = 2.5

    DEFAULT_CSS = """
    PreRenderScreen {
        layout: vertical;
        height: 1fr;
        padding: 0 1;
    }

    #informations {
        width: 70%;
    }
    """

    def __init__(self, episode_file: str, name=None, id=None, classes=None) -> None:
        super().__init__(name, id, classes)
        self.episode_file = episode_file

    def _readable_time(self, seconds: float) -> str:
        h, m = divmod(int(seconds), 3600)
        m, _s = divmod(m, 60)
        return f"{h} hours {m} minutes"

    def compose(self) -> ComposeResult:
        duration_str = self._readable_time(Episode().duration * self.RENDERING_FACTOR)
        yield Center(
            Static(
                "This step will launch After Effects and will build a scene containing "
                "all episode sections. The process could take several minutes. So like "
                "Scott, you should be patient and wait...\n\n"
                "When the script completed, check everything is fine in the scene. "
                "Then you should run the render queue. This rendering is computation "
                f"heavy and could take up to [bold $primary]{duration_str}[/].\n\n"
                f"Prerender file: [bold $primary]{Episode().prerender_file}[/]",
                id="informations",
            )
        )

        with HorizontalGroup():
            yield Button("Cancel", id="cancel")
            yield Button("Launch Pre-Render", variant="primary", id="pre-render")

    def _trigger_pre_render(self) -> None:
        ae_script = generate_ae_script(
            self.episode_file, script_dir=Episode().output_directory
        )
        run_script(ae_script)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "cancel":
            self.app.pop_screen()
        if event.button.id == "pre-render":
            self._trigger_pre_render()
