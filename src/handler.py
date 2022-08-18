import json
import os

import boto3

from form import process_form_post
from models import APIGatewayEvent
from render import render_404, render_ics, render_rsvp_page, render_static_file
from repo import RSVPeaceRepo

DYNAMODB = boto3.resource("dynamodb")
RSVPEACE_TABLE = DYNAMODB.Table(os.environ["RSVPEACE_TABLE"])


def handler(event: dict, context: object):
    if os.environ.get("LOG_LEVEL", "INFO") == "DEBUG":
        print(json.dumps(event))

    api_gw_event = APIGatewayEvent.from_event_dict(event)

    if static_file := render_static_file(api_gw_event):
        return static_file

    repo = RSVPeaceRepo(api_gw_event, RSVPEACE_TABLE)

    if not (attendee := repo.get_attendee()) or not (
        rsvpeace_event := repo.get_rsvpeace_event()
    ):
        return render_404()

    if (
        api_gw_event.http_method == "GET"
        and "download_ics" in api_gw_event.query_string_parameters
    ):
        return render_ics(rsvpeace_event)

    if api_gw_event.http_method == "GET":
        return render_rsvp_page(rsvpeace_event, attendee)

    if api_gw_event.http_method == "POST":
        return process_form_post(api_gw_event, repo)
