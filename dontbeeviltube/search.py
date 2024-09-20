from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import cast

from dateparser import parse as parse_date
from youtubesearchpython import VideosSearch

from dontbeeviltube.util import must, parse_duration


class SearchResult(ABC):
    pass


@dataclass
class Thumbnail:
    url: str
    width: int
    height: int

    @staticmethod
    def from_google(l: list) -> list[Thumbnail]:
        return [
            Thumbnail(
                url=t["url"],
                width=t["width"],
                height=t["height"],
            )
            for t in l
        ]


@dataclass
class VideoSearchResult(SearchResult):

    video_id: str
    title: str
    published_time: datetime
    duration: Decimal
    view_count: int
    thumbnails: list[Thumbnail]
    description_snippet: str
    channel_name: str
    channel_id: str
    channel_thumbnails: list[Thumbnail]


@dataclass
class ChannelSearchResult(SearchResult):
    pass


@dataclass
class PlaylistSearchResult(SearchResult):
    pass


def search_videos(query: str) -> list[VideoSearchResult]:
    return [
        VideoSearchResult(
            video_id=v["id"],
            title=v["title"],
            published_time=must(
                parse_date(v["publishedTime"].removeprefix("Streamed ")),
                f"uninterpretable publish time {v['publishedTime']}",
            ),
            duration=parse_duration(v["duration"]),
            view_count=int(
                v["viewCount"]["text"].removesuffix(" views").replace(",", "")
            ),
            thumbnails=Thumbnail.from_google(v["thumbnails"]),
            description_snippet="".join(p["text"] for p in v["descriptionSnippet"]),
            channel_name=v["channel"]["name"],
            channel_id=v["channel"]["id"],
            channel_thumbnails=Thumbnail.from_google(v["channel"]["thumbnails"]),
        )
        for v in cast(dict, VideosSearch(query).result())["result"]
    ]
