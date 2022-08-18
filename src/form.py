import json

from models import RSVP, APIGatewayEvent
from repo import RSVPeaceRepo


def process_form_post(api_gw_event: APIGatewayEvent, repo: RSVPeaceRepo) -> dict:
    rsvp = RSVP.from_dict(api_gw_event.payload)
    repo.update_rsvp(rsvp)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"success": True}),
    }
