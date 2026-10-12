from dataclasses import dataclass

import yaml

from eval.settings import MANIFEST_PATH


@dataclass(frozen=True)
class Paper:
    id: str
    title: str
    url: str
    sha256: str

    @property
    def filename(self) -> str:
        # Also the filename NoteStream stores, which is how chunks map back to papers.
        return f"{self.id}.pdf"


@dataclass(frozen=True)
class Manifest:
    version: str
    course_name: str
    course_description: str
    papers: tuple[Paper, ...]

    def paper_ids(self) -> set[str]:
        return {paper.id for paper in self.papers}


def load_manifest(path=MANIFEST_PATH) -> Manifest:
    raw = yaml.safe_load(path.read_text())
    return Manifest(
        version=raw["version"],
        course_name=raw["course"]["name"],
        course_description=raw["course"]["description"],
        papers=tuple(
            Paper(id=p["id"], title=p["title"], url=p["url"], sha256=p["sha256"])
            for p in raw["papers"]
        ),
    )
