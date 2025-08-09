from dataclasses import dataclass
import xml.etree.ElementTree as ET
from uuid import uuid4
from genepi.models.episode import Episode

from mutagen.mp4 import MP4
import ffmpeg
import math
import os


def generate_xml(episode: Episode) -> ET.Element:
    e = ET.Element("project")
    ET.SubElement(e, "name")
    children = ET.SubElement(e, "children")

    e.append(_generate_sequence(episode))
    return e


@dataclass
class Sequence:
    id: str
    duration: int


def _generate_sequence(episode: Episode) -> ET.Element:
    seq = ET.Element("sequence")
    seq.attrib["id"]


@dataclass
class Clip:
    LABEL = "Red"

    uuid: str
    framerate: int
    duration: float
    frames: int
    file: str

    def to_xml(self) -> ET.Element:
        e = ET.Element("clip")
        ET.SubElement(e, "uuid").text = self.uuid
        ET.SubElement(e, "duration").text = str(self.frames)
        rate = ET.SubElement(e, "rate")
        ET.SubElement(rate, "timebase").text = str(self.framerate)
        ET.SubElement(rate, "ntsc").text = "FALSE"
        ET.SubElement(e, "name").text = os.path.basename(self.file)
        lbls = ET.SubElement(e, "labels")
        ET.SubElement(lbls, " label2").text = self.LABEL

        return e

@dataclass
class VideoClip(Clip):
    LABEL = "Violet"



    def to_xml(self):
        e = super().to_xml()
        return e


def _generate_video_clip(file:str) -> Clip:
    meta = ffmpeg.probe(file)
    stream = meta["streams"][0]
    duration = float(stream["duration"])
    frames = int(stream["nb_frames"])
    framerate = math.ceil(frames / duration)

    return VideoClip(str(uuid4()), framerate, duration, frames, file)





def _generate_clip(file: str) -> Clip:
    if file.endswith(".mp4")
        return _generate_video_clip(file)


   

e = _generate_clip(
    "/Users/marion/Documents/fantastic-rolls/resources/videos/opening.mp4"
)
print(ET.dump(e.to_xml()))
