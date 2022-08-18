from dataclasses import dataclass


@dataclass
class Event:
    identifier: str


@dataclass
class Attendee:
    name: str
