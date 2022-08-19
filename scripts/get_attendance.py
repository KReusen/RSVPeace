import argparse
import json
from collections import defaultdict
from typing import Iterable

import boto3
from boto3.dynamodb.types import TypeDeserializer


def create_details(responses: list[dict]) -> dict[str, list]:
    result = defaultdict(list)
    for attendee in responses:
        if (is_going := attendee["rsvp"].get("going")) is True:
            guests = [
                f"{attendee['nickname']}_guest_{i}"
                for i in range(1, int(attendee["rsvp"].get("plusones", 0)) + 1)
            ]
            result["going"] += [attendee["nickname"]] + guests
        elif is_going is False:
            result["not_going"].append(attendee["nickname"])
        else:
            result["unknown"].append(attendee["nickname"])

    return result


def write_details_to_file(details: dict[str, list], filepath: str) -> None:
    with open(filepath, "w") as fh:
        json.dump(details, fh, indent=4)


def create_summary(details: dict[str, list]) -> dict[str, int]:
    return {k: len(v) for k, v in details.items()}


def deserialize_responses(response_pages: Iterable[dict]) -> list[dict]:
    deserializer = TypeDeserializer()
    return [
        deserialize_item(item, deserializer)
        for p in response_pages
        for item in p["Items"]
    ]


def deserialize_item(
    item: dict, deserializer: TypeDeserializer = TypeDeserializer()
) -> dict:
    return {k: deserializer.deserialize(v) for k, v in item.items()}


def main(
    event_slug: str,
    dynamodb_table_name: str,
    output_path: str,
):
    paginator = boto3.client("dynamodb").get_paginator("query")
    response_pages = paginator.paginate(
        TableName=dynamodb_table_name,
        KeyConditionExpression="event_slug = :event_slug_val AND begins_with(details , :details_val)",
        ExpressionAttributeValues={
            ":event_slug_val": {"S": event_slug},
            ":details_val": {"S": "attendee#"},
        },
    )

    deserialized_responses = deserialize_responses(response_pages)

    details = create_details(deserialized_responses)
    write_details_to_file(details, output_path)

    summary = create_summary(details)
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python get_attendance.py",
        description="Prints a summary for a given event and writes detailed attendance information to a json file.",
    )
    parser.add_argument(
        "-e",
        "--event_slug",
        help="The event_slug you're looking up attendance for",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dynamo_table_name",
        help="The name of the dynamodb table you want to read from",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="The name of the file you want to write the detailed attendance information to.",
        default="attendance_details.json",
    )
    args = parser.parse_args()
    main(args.event_slug, args.dynamo_table_name, args.output_file)
