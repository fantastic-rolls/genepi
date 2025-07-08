from typing import Optional
from uuid import uuid4

from textual import on, work
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Button, Input
from textual_fspicker import FileOpen, Filters, SelectDirectory


class DirectoryPicker(HorizontalGroup):
    DEFAULT_CSS = """
    Button {
        dock: right;
    }
    """

    def __init__(
        self,
        callback: Optional[callable] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        value: Optional[str] = None,
        placeholder: str = "",
    ) -> None:
        if id is None:
            id = f"dp_{uuid4().hex}"
        super().__init__(id=id, classes=classes)
        self.callback = callback
        self.value = value
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield Button(
            "Select...",
            classes="directory_path_btn",
            id=f"{self.id}_btn",
        )
        yield Input(
            disabled=True,
            classes="directory_path",
            id=f"{self.id}_lbl",
            value=self.value,
            placeholder=self.placeholder,
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()

    @on(Button.Pressed)
    @work
    async def pick_a_directory(self) -> None:
        if opened := await self.app.push_screen_wait(SelectDirectory()):
            self.query_one(f"#{self.id}_lbl", Input).value = str(opened)
            if self.callback:
                self.callback(str(opened))


class FilePicker(HorizontalGroup):
    DEFAULT_CSS = """
    Button {
        dock: right;
    }
    """

    def __init__(
        self,
        callback: Optional[callable] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        placeholder: str = "",
        value: Optional[str] = None,
        filters: Optional[dict[str, list[str]]] = None,
    ) -> None:
        if id is None:
            id = f"dp_{uuid4().hex}"
        super().__init__(id=id, classes=classes)
        self.callback = callback
        self.placeholder = placeholder
        self.value = value
        self.filters = []
        for f_name, f_exts in (filters or {}).items():
            if not f_exts:
                continue
            self.filters.append((f_name, lambda p: p.suffix.lower() in f_exts))
        self.filters.append(("All", lambda _: True))

    def compose(self) -> ComposeResult:
        yield Button(
            "Select...",
            classes="directory_path_btn",
            id=f"{self.id}_btn",
        )
        yield Input(
            disabled=True,
            classes="directory_path",
            id=f"{self.id}_lbl",
            value=self.value,
            placeholder=self.placeholder,
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()

    @on(Button.Pressed)
    @work
    async def pick_a_directory(self) -> None:
        if opened := await self.app.push_screen_wait(
            FileOpen(filters=Filters(*self.filters))
        ):
            self.query_one(f"#{self.id}_lbl", Input).value = str(opened)
            if self.callback:
                self.callback(str(opened))
