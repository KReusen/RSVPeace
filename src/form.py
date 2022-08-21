import json

from models import RSVP
from repo import RSVPeaceRepo


def process_form_post(payload: dict, repo: RSVPeaceRepo) -> dict:
    rsvp = RSVP.from_dict(payload)
    repo.update_rsvp(rsvp)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"success": True}),
    }
