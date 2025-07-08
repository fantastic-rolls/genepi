import uuid
from typing import ClassVar, Final, Optional, Type

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.screen import Screen
from textual.widgets import (
    Button,
    Input,
)

from genepi.components.helpers import make_panel_view
from genepi.components.resources_view import ResourcePanel
from genepi.components.Widgets.directory_picker import DirectoryPicker, FilePicker
from genepi.models.episode import Episode
from genepi.services import (
    AudioResource,
    AudioService,
    BaseResource,
    PanelResource,
    PanelService,
    ResourceService,
    ResourceWalker,
    SectionResource,
)


class PrepareGeneral(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Title", id="episode_title_input")
        yield Input(placeholder="SubTitle", id="episode_subtitle_input")
        yield DirectoryPicker(
            placeholder="Output directory", callback=self.handle_episode_output
        )

    def on_input_changed(self, message: Input.Changed) -> None:
        message.stop()
        handlers = {
            "episode_title_input": self.handle_episode_title,
            "episode_subtitle_input": self.handle_episode_subtitle,
        }

        handler = handlers.get(message.input.id)
        if not handler:
            raise ValueError(f"No handler for input '{message.input.id}'")
        handler(message.value)

    def handle_episode_title(self, title: str) -> None:
        Episode().title = title

    def handle_episode_subtitle(self, subtitle: str) -> None:
        Episode().subtitle = subtitle

    def handle_episode_output(self, directory: str) -> None:
        Episode().output_directory = directory


class PrepareResources(VerticalGroup):
    SERVICE: ClassVar[Type[ResourceService]] = None
    RESOURCE_TYPE: ClassVar[Type[BaseResource]] = None
    PLACEHOLDER: ClassVar[str] = ""

    def __init__(
        self,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self._service = self.SERVICE()
        self._internal_id = uuid.uuid4().hex

    def compose(self) -> ComposeResult:
        yield DirectoryPicker(
            placeholder=self.PLACEHOLDER, callback=self.handle_directory_selected
        )
        yield ResourcePanel(
            self.RESOURCE_TYPE,
            id=f"resource_list_{self._internal_id}",
            classes="resource-panel",
        )

    def handle_directory_selected(self, directory: str) -> None:
        resource_list = self.query_one(
            f"#resource_list_{self._internal_id}", ResourcePanel
        )
        walker = ResourceWalker(self._service)
        walker.process(directory)
        resource_list.set_resources(self._service.all())


class PrepareAudios(PrepareResources):
    SERVICE: Final[Type[ResourceService]] = AudioService
    RESOURCE_TYPE: Final[Type[BaseResource]] = AudioResource
    PLACEHOLDER: Final[str] = "Audio tracks directory"

    def handle_directory_selected(self, directory: str) -> None:
        super().handle_directory_selected(directory)
        Episode().audio_tracks = {
            (a.character.lower() if a.character else "master"): a
            for a in self._service.all()
        }


class PreparePanels(PrepareResources):
    SERVICE: Final[Type[ResourceService]] = PanelService
    RESOURCE_TYPE: Final[Type[BaseResource]] = PanelResource
    PLACEHOLDER: Final[str] = "Panels directory"


class PrepareSections(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield FilePicker(
            placeholder="Audacity sections file",
            callback=self.handle_file_selected,
            filters={"Audacity sections": [".txt"]},
        )
        yield ResourcePanel(
            SectionResource,
            id="resource_list_sections",
            classes="resource-panel",
        )

    def handle_file_selected(self, file: str) -> None:
        resource_list = self.query_one("#resource_list_sections", ResourcePanel)
        sections = SectionResource.read_file(file)
        resource_list.set_resources(sections)
        Episode().sections = sections


class PrepareScreen(Screen):
    BINDINGS: Final = [("escape", "app.pop_screen", "Pop screen")]

    DEFAULT_CSS = """
    PrepareScreen {
        layout: vertical;
        height: 1fr;
        padding: 0 1;
    }
    #footer {
        padding: 2;
        dock: bottom;
        align: right middle;
    }
    #footer Button {
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            yield make_panel_view("General", PrepareGeneral())
            yield make_panel_view("Audio tracks", PrepareAudios())
            yield make_panel_view("Panels", PreparePanels())
            yield make_panel_view("Audacity sections", PrepareSections())
        with HorizontalGroup(id="footer"):
            yield Button("Cancel", id="cancel")
            yield Button("Generate", variant="primary", id="generate")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "cancel":
            self.app.pop_screen()
        if event.button.id == "generate":
            Episode().write_file()
