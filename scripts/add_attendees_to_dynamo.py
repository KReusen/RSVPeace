import argparse
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.exceptions import ClientError


@dataclass
class Attendee:
    full_name: str
    nickname: str
    _cached_identifier: Optional[str] = None

    @property
    def identifier(self) -> str:
        if not self._cached_identifier:
            self._cached_identifier = self._create_identifier()
        return self._cached_identifier

    def _create_identifier(self) -> str:
        raise NotImplementedError(
            "Please come up with your own desired way of creating identifiers"
        )

    def to_csv_line(self) -> str:
        return f"{self.full_name},{self.nickname},{self.identifier}\n"

    def to_dynamodb_dict(self) -> dict:
        return {
            "details": f"attendee#{self.identifier}",
            "nickname": self.nickname,
            "rsvp": {},
        }


def add_to_dynamodb_if_not_exists(
    attendee: Attendee, event_slug: str, table: object
) -> None:
    attendee_dict = attendee.to_dynamodb_dict()

    try:
        table.put_item(
            Item={"event_slug": event_slug, **attendee_dict},
            ConditionExpression="event_slug <> :event_slug AND details <> :details",
            ExpressionAttributeValues={
                ":event_slug": event_slug,
                ":details": attendee_dict["details"],
            },
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise e


def read_attendees_from_file(filepath: str) -> list[Attendee]:
    with open(filepath) as fh:
        return [Attendee(*line.split(",")) for line in fh.read().splitlines()]


def write_attendees_to_file(attendees: list[Attendee], filepath: str) -> None:
    with open(filepath, "w") as fh:
        fh.writelines([attendee.to_csv_line() for attendee in attendees])


def main(
    attendees_input_path: str,
    event_slug: str,
    dynamodb_table_name: str,
    output_path: str,
):
    attendees = read_attendees_from_file(attendees_input_path)

    dynamodb_table = boto3.resource("dynamodb").Table(dynamodb_table_name)
    for attendee in attendees:
        add_to_dynamodb_if_not_exists(attendee, event_slug, dynamodb_table)

    # write the attendees and their identifiers to a file. This helps with contacting them later and building links for them.
    write_attendees_to_file(attendees, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python add_invitees_to_dynamo.py",
        description="Looks at a csv file with full_name,nickname data, generates idempotent identifiers for each record and store the record in DynamoDB if it did not exist before",
    )
    parser.add_argument(
        "-i",
        "--input_file",
        help="A csv file with full_name,nickname columns",
        required=True,
    )
    parser.add_argument(
        "-e",
        "--event_slug",
        help="The event_slug these attendees need to be invited for",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dynamo_table_name",
        help="The name of the dynamodb table you want to write to",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="The name of the file you want to write the created attendees to",
        default="attendees_with_identifiers.csv",
    )
    args = parser.parse_args()
    main(args.input_file, args.event_slug, args.dynamo_table_name, args.output_file)
