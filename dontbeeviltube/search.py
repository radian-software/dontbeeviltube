from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Sequence
from urllib.parse import urlencode

from dateparser import parse as parse_date
import requests

from dontbeeviltube.util import must, parse_amount, parse_duration


class Magic:

    CONTEXT = {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20210224.06.00",
            "newVisitorCookie": True,
        },
        "user": {
            "lockedSafetyMode": False,
        },
    }

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"

    SEARCH_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"


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
class Video:

    id: str
    title: str
    published_time: datetime
    duration: Decimal
    view_count: int
    thumbnails: list[Thumbnail]
    description_snippet: str
    channel_name: str
    channel_id: str
    channel_thumbnails: list[Thumbnail]

    type: str = "video"

    @property
    def duration_str(self) -> str:
        dur = int(self.duration)
        parts = []
        while dur:
            parts.append(dur % 60)
            dur //= 60
        return ":".join(f"{p:02d}" for p in reversed(parts))


@dataclass
class Channel:

    id: str
    title: str
    subscriber_count: int
    thumbnails: list[Thumbnail]
    description_snippet: str

    type: str = "channel"


@dataclass
class Playlist:

    id: str
    title: str
    video_count: int
    thumbnails: list[Thumbnail]
    channel_name: str
    channel_id: str

    type: str = "playlist"


def lookup(obj: Any, path: Sequence[str | int]) -> Any:
    if not path:
        return obj
    return lookup(obj[path[0]], path[1:])


def search(query: str) -> list[Video | Channel]:
    queryparams = {
        "key": Magic.SEARCH_KEY,
    }
    resp = requests.post(
        f"https://www.youtube.com/youtubei/v1/search?{urlencode(queryparams)}",
        headers={
            "user-agent": Magic.USER_AGENT,
        },
        json={
            "query": query,
            "context": Magic.CONTEXT,
            "client": {
                "hl": "en",
                "gl": "us",
            },
        },
    )
    resp.raise_for_status()
    results = []
    content = lookup(
        resp.json(),
        [
            "contents",
            "twoColumnSearchResultsRenderer",
            "primaryContents",
            "sectionListRenderer",
            "contents",
        ],
    )
    for item in content:
        if sect := item.get("itemSectionRenderer"):
            for item in sect["contents"]:
                try:
                    if elt := item.get("videoRenderer"):
                        results.append(
                            Video(
                                id=elt["videoId"],
                                title=lookup(elt, ["title", "runs", 0, "text"]),
                                published_time=must(
                                    parse_date(
                                        raw_published_time := lookup(
                                            elt, ["publishedTimeText", "simpleText"]
                                        ).removeprefix("Streamed "),
                                    ),
                                    f"uninterpretable publish time {raw_published_time}",
                                ),
                                duration=parse_duration(
                                    lookup(elt, ["lengthText", "simpleText"])
                                ),
                                view_count=int(
                                    lookup(elt, ["viewCountText", "simpleText"])
                                    .removesuffix(" views")
                                    .replace(",", "")
                                ),
                                thumbnails=Thumbnail.from_google(
                                    lookup(
                                        elt,
                                        ["thumbnail", "thumbnails"],
                                    )
                                ),
                                description_snippet=elt.get("detailedMetadataSnippets")
                                and "".join(
                                    p["text"]
                                    for p in lookup(
                                        elt,
                                        [
                                            "detailedMetadataSnippets",
                                            0,
                                            "snippetText",
                                            "runs",
                                        ],
                                    )
                                ),
                                channel_name=lookup(
                                    elt, ["ownerText", "runs", 0, "text"]
                                ),
                                channel_id=lookup(
                                    elt,
                                    [
                                        "ownerText",
                                        "runs",
                                        0,
                                        "navigationEndpoint",
                                        "browseEndpoint",
                                        "browseId",
                                    ],
                                ),
                                channel_thumbnails=Thumbnail.from_google(
                                    lookup(
                                        elt,
                                        [
                                            "channelThumbnailSupportedRenderers",
                                            "channelThumbnailWithLinkRenderer",
                                            "thumbnail",
                                            "thumbnails",
                                        ],
                                    )
                                ),
                            )
                        )
                    elif elt := item.get("channelRenderer"):
                        results.append(
                            Channel(
                                id=elt["channelId"],
                                title=lookup(elt, ["title", "simpleText"]),
                                subscriber_count=parse_amount(
                                    lookup(
                                        elt, ["videoCountText", "simpleText"]
                                    ).removesuffix(" subscribers")
                                ),
                                thumbnails=Thumbnail.from_google(
                                    lookup(elt, ["thumbnail", "thumbnails"])
                                ),
                                description_snippet="".join(
                                    p["text"]
                                    for p in lookup(elt, ["descriptionSnippet", "runs"])
                                ),
                            )
                        )
                    elif elt := item.get("lockupViewModel"):
                        assert elt["contentType"] == "LOCKUP_CONTENT_TYPE_PLAYLIST"
                        results.append(
                            Playlist(
                                id=elt["contentId"],
                                title=lookup(
                                    elt,
                                    [
                                        "metadata",
                                        "lockupMetadataViewModel",
                                        "title",
                                        "content",
                                    ],
                                ),
                                video_count=int(
                                    lookup(
                                        elt,
                                        [
                                            "contentImage",
                                            "collectionThumbnailViewModel",
                                            "primaryThumbnail",
                                            "thumbnailViewModel",
                                            "overlays",
                                            0,
                                            "thumbnailOverlayBadgeViewModel",
                                            "thumbnailBadges",
                                            0,
                                            "thumbnailBadgeViewModel",
                                            "text",
                                        ],
                                    ).removesuffix(" videos")
                                ),
                                thumbnails=Thumbnail.from_google(
                                    lookup(
                                        elt,
                                        [
                                            "contentImage",
                                            "collectionThumbnailViewModel",
                                            "primaryThumbnail",
                                            "thumbnailViewModel",
                                            "image",
                                            "sources",
                                        ],
                                    )
                                ),
                                channel_name=lookup(
                                    elt,
                                    [
                                        "metadata",
                                        "lockupMetadataViewModel",
                                        "metadata",
                                        "contentMetadataViewModel",
                                        "metadataRows",
                                        0,
                                        "metadataParts",
                                        0,
                                        "text",
                                        "content",
                                    ],
                                ),
                                channel_id=lookup(
                                    elt,
                                    [
                                        "metadata",
                                        "lockupMetadataViewModel",
                                        "metadata",
                                        "contentMetadataViewModel",
                                        "metadataRows",
                                        0,
                                        "metadataParts",
                                        0,
                                        "text",
                                        "commandRuns",
                                        0,
                                        "onTap",
                                        "innertubeCommand",
                                        "browseEndpoint",
                                        "browseId",
                                    ],
                                ),
                            )
                        )
                    elif item.get("shelfRenderer"):
                        pass  # not needed
                    elif item.get("reelShelfRenderer"):
                        pass  # this is not fucking tiktok
                    else:
                        raise RuntimeError("could not identify type of search result")
                except Exception as e:
                    raise RuntimeError(
                        f"failed to parse search result, original data: {item}"
                    ) from e
    return results
