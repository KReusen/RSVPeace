from typing import Optional

from boto3.dynamodb.conditions import Key

from models import RSVP, APIGatewayEvent, Attendee, RSVPeaceEvent


class RSVPeaceRepo:
    def __init__(self, api_gw_event: APIGatewayEvent, dynamodb_table: object):
        self.api_gw_event = api_gw_event
        self.dynamodb_table = dynamodb_table

    def get_attendee(self) -> Optional[Attendee]:
        response = self.dynamodb_table.query(
            KeyConditionExpression=Key("event_slug").eq(self.api_gw_event.event_slug)
            & Key("details").eq(f"attendee#{self.api_gw_event.attendee_id}")
        )

        if response["Count"] != 1:
            return

        attendee = response["Items"][0]
        return Attendee(
            identifier=self.api_gw_event.attendee_id,
            nickname=attendee["nickname"],
            rsvp=RSVP.from_dict(attendee.get("rsvp", {})),
        )

    def get_rsvpeace_event(self) -> Optional[RSVPeaceEvent]:
        response = self.dynamodb_table.query(
            KeyConditionExpression=Key("event_slug").eq(self.api_gw_event.event_slug)
            & Key("details").eq("event")
        )

        if response["Count"] != 1:
            return

        rsvpeace_event = response["Items"][0]
        return RSVPeaceEvent(
            slug=self.api_gw_event.event_slug,
            title=rsvpeace_event["title"],
            address=rsvpeace_event["address"],
            start=rsvpeace_event["start"],
            end=rsvpeace_event["end"],
            html_date=rsvpeace_event["html_date"],
            html_description=rsvpeace_event["html_description"],
            html_gift_message=rsvpeace_event["html_gift_message"],
        )

    def update_rsvp(self, rsvp: RSVP) -> None:
        self.dynamodb_table.update_item(
            Key={
                "event_slug": self.api_gw_event.event_slug,
                "details": f"attendee#{self.api_gw_event.attendee_id}",
            },
            UpdateExpression="SET rsvp = :new_rsvp",
            ExpressionAttributeValues={":new_rsvp": rsvp.to_dict()},
        )
