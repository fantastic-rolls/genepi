from typing import ClassVar, Type

from rich.text import Text
from textual.events import Resize
from textual.reactive import reactive
from textual.widgets import DataTable

from genepi.models.configuration import Configuration
from genepi.services import (
    AudioResource,
    BaseResource,
    LabelsResource,
    PanelResource,
    SectionResource,
)
from genepi.utils import seconds_to_timecode


def make_panel_rows(res: list[PanelResource]) -> list[tuple]:
    rows = [("Start", "End", "Count", "Image", "Path")]
    conf = Configuration()
    rows.extend(
        [
            (
                f"[bold]{seconds_to_timecode(r.start)}[/]",
                f"""[bold]{
                    seconds_to_timecode(
                        r.end if r.end else r.start + r.count * conf.panel_duration
                    )
                }[/]""",
                r.count,
                "Yes" if r.has_image else "No",
                r.aggregated_path,
            )
            for r in res
        ]
    )
    return rows


def make_audio_rows(res: list[AudioResource]) -> list[tuple]:
    rows = [("Character", "Duration", "Size", "Path")]
    rows.extend(
        [
            (r.character or "Master", seconds_to_timecode(r.duration), r.size, r.path)
            for r in res
        ]
    )
    return rows


def make_label_rows(res: list[LabelsResource]) -> list[tuple]:
    rows = [("Labels", "Regions", "Path")]
    print([r.path for r in res])
    rows.extend([(len(r.tags), len(r.regions), r.path) for r in res])
    return rows


def make_section_rows(res: list[SectionResource]) -> list[tuple]:
    rows = [("Start", "End", "Is tag", "Type", "Extras")]
    rows.extend(
        [
            (
                seconds_to_timecode(r.start),
                seconds_to_timecode(r.end),
                r.is_tag,
                r.type.value,
                ", ".join([f"{k}={v}" for k, v in r.extras.items()]),
            )
            for r in res
        ]
    )
    return rows


class ResourcePanel(DataTable):
    DEFAULT_CSS = """
    ResourcePanel {
        min-height: 10;
    }
    """

    ROWS_FACTORY: ClassVar[dict] = {
        AudioResource: make_audio_rows,
        PanelResource: make_panel_rows,
        LabelsResource: make_label_rows,
        SectionResource: make_section_rows,
    }

    resources: reactive[list[BaseResource]] = reactive([])

    def __init__(
        self,
        resource_type: Type[BaseResource],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            show_header=True,
            show_row_labels=True,
            zebra_stripes=True,
            name=name,
            id=id,
            classes=classes,
        )
        self.cursor_type = "row"
        self._resource_type = resource_type
        self._factory = self.ROWS_FACTORY.get(self._resource_type)
        self._rows = []
        self.set_resources([])
        if not self._factory:
            raise ValueError(f"No factory defined for resource '{self._resource_type}'")

    def set_resources(self, resources: list[BaseResource]) -> None:
        self.resources = [r for r in resources if isinstance(r, self._resource_type)]
        rows = self._factory(self.resources)
        self.clear()
        if not self.columns:
            self.add_columns(*rows[0])
        for i, row in enumerate(rows[1:]):
            label = Text(str(i), style="#B0FC38 italic")
            self.add_row(*row, label=label)
        self._update_columns_size(self.window_region.width)

    def _update_columns_size(self, new_width: int) -> None:
        width = 0
        columns = [c for c in self.columns.values()]
        for c in columns[:-1]:
            width += c.width
        # Add padding
        width += 2 * (self.cell_padding * len(self.columns))
        last_col = columns[-1]
        last_col.auto_width = False
        last_col.width = new_width - width

        self.refresh()

    def on_resize(self, event: Resize) -> None:
        self._update_columns_size(event.size.width)
