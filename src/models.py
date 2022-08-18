import json
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class APIGatewayEvent:
    path: str
    event_slug: str
    attendee_id: str
    http_method: str
    body: str
    query_string_parameters: dict[str, str]

    @property
    def payload(self) -> dict:
        return json.loads(self.body)

    @classmethod
    def from_event_dict(cls, d: dict) -> "APIGatewayEvent":
        return cls(
            path=d["path"],
            event_slug=d["requestContext"]["domainPrefix"].lower(),
            attendee_id=d["pathParameters"]["proxy"].lower().replace("-", ""),
            http_method=d["httpMethod"],
            body=d.get("body") or "{}",
            query_string_parameters=d.get("queryStringParameters") or {},
        )


@dataclass
class RSVP:
    going: Optional[bool]
    plusones: Optional[int]

    @property
    def nr_plusones(self) -> int:
        return self.plusones or 0

    @property
    def yes_is_checked(self) -> str:
        return "checked" if self.going is True else ""

    @property
    def no_is_checked(self) -> str:
        return "checked" if self.going is False else ""

    @classmethod
    def from_dict(cls, d: dict) -> "RSVP":
        temp = {"going": d.get("going"), "plusones": int(d.get("plusones", 0))}

        # always set plusones to None when someone is not going
        if not temp["going"]:
            temp["plusones"] = None

        return cls(**temp)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class RSVPeaceEvent:
    slug: str
    title: str
    address: str
    start: str
    end: str
    html_date: str
    html_description: str
    html_gift_message: str

    @staticmethod
    def _iso_date_to_vcal_date(dt: str) -> str:
        return dt.replace("-", "").replace(":", "")

    @property
    def vcal_start(self) -> str:
        return self._iso_date_to_vcal_date(self.start)

    @property
    def vcal_end(self) -> str:
        return self._iso_date_to_vcal_date(self.end)


@dataclass
class Attendee:
    identifier: str
    nickname: str
    rsvp: RSVP
