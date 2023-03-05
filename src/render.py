from models import APIGatewayEvent, Attendee, DisplayEventAndAttendee, RSVPeaceEvent


def render_404() -> dict:
    with open("templates/404.html") as fh:
        error_page = fh.read()

    return {
        "statusCode": 404,
        "headers": {"Content-Type": "text/html"},
        "body": error_page,
    }


def render_rsvp_page(event: RSVPeaceEvent, attendee: Attendee) -> dict:
    with open("templates/index.html") as fh:
        index = fh.read()

    data = DisplayEventAndAttendee(event=event, attendee=attendee)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": index.format(data=data),
    }


def render_static_file(event: APIGatewayEvent) -> dict:
    allowed_static_files = {"/static/main.js": "application/javascript"}

    if event.path in allowed_static_files:
        with open(event.path.removeprefix("/")) as fh:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": allowed_static_files[event.path]},
                "body": fh.read(),
            }


def render_ics(event: RSVPeaceEvent) -> dict:
    with open("templates/event.ics") as fh:
        ics = fh.read()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/calendar"},
        "body": ics.format(event=event),
    }
