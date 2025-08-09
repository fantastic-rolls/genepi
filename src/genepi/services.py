import re
from collections import Counter
from enum import Enum
from math import ceil
from os import listdir
from os.path import basename, dirname, isfile, join
from typing import ClassVar, Generator, Optional

import audio_metadata
from typing_extensions import Self

from genepi.utils import bytes_to_mb, timecode_to_seconds


class Sections(str, Enum):
    undefined = "undefined"
    lobby = "lobby"
    roleplay = "roleplay"
    fight = "fight"
    question = "questions"
    opening = "opening"


class BaseResource:
    __resource_ids: ClassVar[Counter] = Counter()

    @classmethod
    def get_id(cls) -> int:
        cls.__resource_ids[cls.__class__.__name__] += 1
        return cls.__resource_ids[cls.__class__.__name__]

    def __init__(self, path: str, name: Optional[str] = None) -> None:
        self.path = path
        self.name = name or f"{self.__class__.__name__}_{self.get_id()}"


class PanelResource(BaseResource):
    def __init__(
        self,
        path: str,
        start: int,
        count: int,
        has_image: bool,
        end: Optional[int] = None,
    ) -> None:
        super().__init__(path)
        self.start = start
        self.end = end
        self.count = count
        self.has_image = has_image

    def use_image(self) -> None:
        self.has_image = True

    def add_sub_panel(self) -> None:
        self.count += 1

    @property
    def aggregated_path(self) -> str:
        sub_ids = [str(i) for i in range(1, self.count + 1)]
        if self.has_image:
            sub_ids.append("img")
        base = basename(self.path)
        parts = base[:-4].split("_")
        parts[2] = f"{{{','.join(sub_ids)}}}"
        aggregated = "_".join(parts) + base[-4:]
        return "/".join([dirname(self.path), aggregated])


class AudioResource(BaseResource):
    def __init__(
        self, path: str, character: str | None, duration: int, size: int
    ) -> None:
        super().__init__(path)
        self.character = character
        self.duration = duration
        self.size = size

    @classmethod
    def factory(cls, path: str, character: str | None) -> Self:
        metadata = audio_metadata.load(path)
        duration = ceil(metadata["streaminfo"]["duration"])
        return AudioResource(
            path,
            character,
            duration,
            bytes_to_mb(metadata.filesize),
        )


class LabelsResource(BaseResource):
    def __init__(self, path: str, tags: int, regions: str) -> None:
        super().__init__(path)
        self.tags = (tags,)
        self.regions = regions


class SectionResource(BaseResource):
    def __init__(self, start: float, end: Optional[float], payload: str) -> None:
        super().__init__("")
        self.start = start
        self.end = end
        self.payload = payload
        self.type = Sections.undefined
        self.extras = {}
        self._parse_payload()

    def _parse_payload(self) -> None:
        section_type, *parts = self.payload.split(";")
        try:
            self.type = Sections(section_type.lower())
        except ValueError:
            return
        # Handle extras
        for part in parts:
            key, value = part.split("=", 1)
            self.extras[key] = value

    @property
    def is_tag(self) -> bool:
        return self.start == self.end

    @classmethod
    def read_file(cls, file: str) -> list[Self]:
        sections = []
        with open(file, "r", encoding="utf-8") as fp:
            for line in fp.readlines():
                if not line:
                    continue
                start, end, payload = line.split("\t", 3)
                sections.append(
                    SectionResource(float(start), float(end), payload.strip())
                )
        return sections


class ResourceService:
    patterns = re.compile(".+")

    def __init__(self) -> None:
        self._resources = {}

    def process(self, path: str) -> None:
        matches = re.match(self.pattern, basename(path))
        if not matches:
            return
        self._register(path, matches)

    def _register(self, path: str, matches: re.Match[str]) -> None:
        raise NotImplementedError()

    def reset(self) -> None:
        self._resources = {}

    def all(self) -> Generator[BaseResource, None, None]:
        print(self._resources)
        for item in self._resources.values():
            print(f"{item=}")
            yield item


class AudioService(ResourceService):
    pattern = re.compile("session(\d+)-master(-(.+))?\\.mp3")

    def _register(self, path: str, matches: re.Match[str]) -> None:
        character = matches.group(3)
        self._resources[character] = AudioResource.factory(path, character)


class PanelService(ResourceService):
    pattern = re.compile("panel_(\d+-\d+-\d+)(_(\d+-\d+-\d+))?_(\d+|img).png")

    def _register(self, path: str, matches: re.Match[str]) -> None:
        start = timecode_to_seconds(matches.group(1))
        end = matches.group(3)
        end = timecode_to_seconds(end) if end else None
        res: PanelResource = self._resources.setdefault(
            start, PanelResource(path, start, 0, False, end=end)
        )
        try:
            int(matches.group(4))
            res.add_sub_panel()
        except ValueError:
            res.use_image()


class ResourceWalker:
    def __init__(self, *services: ResourceService) -> None:
        self.__services = services

    def process(self, path: str) -> None:
        for service in self.__services:
            service.reset()

        for entry in listdir(path):
            entry = join(path, entry)
            if not isfile(entry):
                continue
            for service in self.__services:
                service.process(entry)
