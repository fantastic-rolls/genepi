import json
import os
from hashlib import md5

from genepi.models.configuration import Configuration
from genepi.services import AudioResource, SectionResource, Sections
from genepi.utils import Singleton


class Episode(metaclass=Singleton):
    def __init__(self) -> None:
        self.season = 0
        self.episode = 0
        self.title = ""
        self.subtitle = ""
        self.template = ""
        self.output_directory = ""
        self.audio_tracks: dict[str, AudioResource] = {}
        self.panels = []
        self.sections: list[SectionResource] = []
        self.output_directory = ""

    @property
    def players(self) -> int:
        players = 0
        for p in self.audio_tracks:
            if p.lower() not in ("master", "narrator"):
                players += 1
        return players

    @property
    def duration(self) -> float:
        return max([0, *[a.duration for a in self.audio_tracks.values()]])

    @property
    def prerender_name(self) -> str:
        return md5(f"{self.title}-{self.subtitle}".encode("utf-8")).hexdigest()

    @property
    def prerender_file(self) -> str:
        return os.path.join(self.output_directory, f"{self.prerender_name}.mp4")

    def section_to_dict(self, section: SectionResource) -> dict:
        mandatory_extras = {}
        if section.type in (Sections.fight, Sections.question, Sections.roleplay):
            mandatory_extras["players"] = self.players
        if section.type == Sections.lobby:
            mandatory_extras["audio"] = "narrator"

        data = {
            "name": section.name,
            "start": section.start,
            "end": section.end,
            "type": section.type.value,
            "payload": {**mandatory_extras, **section.extras},
        }

        if "audio" in data["payload"]:
            # Resolve
            track = self.audio_tracks.get(data["payload"]["audio"])
            if track:
                data["payload"]["audio"] = track.path
        return data

    def audio_to_dict(self) -> dict[str, str]:
        return {k: v.path for k, v in self.audio_tracks.items()}

    def write_file(self, file: str = "episode.json") -> None:
        data = {
            "title": self.title,
            "subtitle": self.subtitle,
            "duration": self.duration,
            "output": self.output_directory,
            "sections": [],
            "audios": self.audio_to_dict(),
            "template": Configuration().after_effects_template,
            "prerender": self.prerender_file,
            "prerender_project": f"{self.prerender_file}.aep",
        }

        for section in self.sections:
            data["sections"].append(self.section_to_dict(section))

        with open(
            os.path.join(self.output_directory, file), "w", encoding="utf-8"
        ) as fp:
            json.dump(data, fp, indent=4, separators=(",", ": "))

    def _load_audio_tracks(self, tracks: dict[str, str]) -> None:
        for name, file in tracks.items():
            self.audio_tracks[name] = AudioResource.factory(file, name)

    def load_file(self, file: str) -> None:
        with open(file, "r", encoding="utf-8") as fp:
            data = json.load(fp)

            self.title = data.get("title", "")
            self.subtitle = data.get("subtitle", "")
            self.output_directory = data.get("output", "")
            self.template = data.get("template", "")
            self.audio_tracks = {}
            self._load_audio_tracks(data.get("audios", {}))
