#!/usr/bin/env python3

import argparse
import random
import sys
import io
import traceback
from textwrap import indent
from typing import Union
import requests
import tweepy

PETFINDER_TOKEN_URL = "https://api.petfinder.com/v2/oauth2/token"
PETFINDER_API_URL = "https://api.petfinder.com/v2/animals"
MAX_ATTEMPTS = 3

DEFAULT_NAMES = ["pup", "pupper", "doggie", "cutie"]
SINGLE_END_PHRASES = [
    "needs a loving home!",
    "is looking for a new family!",
    "is looking for a furever home!",
    "needs a new best friend!",
    "needs a place to call home!",
    "is looking for a forever home!",
    "wants to be your buddy!",
    "is looking for a loving family!",
    "is in need of love!",
    "is in need of a loving home!",
    "is looking for a new home!",
    "needs some lovin'!",
    "could be your new buddy!",
]
MULTIPLE_END_PHRASES = [
    "need a loving home!",
    "are looking for a new family!",
    "are looking for a furever home!",
    "need a new best friend!",
    "need a place to call home!",
    "are looking for a forever home!",
    "want to be your buddy!",
    "are looking for a loving family!",
    "are in need of love!",
    "are in need of a loving home!",
    "are looking for a new home!",
    "need some lovin'!",
    "could be your new buddies!",
]


def print_indented(msg: str, indent_levels: int = 1) -> None:
    print(indent(msg, " " * 4 * indent_levels))


def get_cli_args() -> dict:
    parser = argparse.ArgumentParser(
        description="🐶 Find adoptable dogs looking for a loving home"
    )
    parser.add_argument(
        "--petfinder_api_key",
        help="Your key for the Petfinder API",
        required=True,
    )
    parser.add_argument(
        "--petfinder_secret",
        help="Your secret for the Petfinder API",
        required=True,
    )
    parser.add_argument(
        "--twitter_api_key",
        help="Your key for the Twitter v2 API",
        required=True,
    )
    parser.add_argument(
        "--twitter_api_secret",
        help="Your secret for the Twitter v2 API",
        required=True,
    )
    parser.add_argument(
        "--twitter_access_token",
        help="Your access token for your Twitter v2 developer account",
        required=True,
    )
    parser.add_argument(
        "--twitter_access_token_secret",
        help="Your access token secret for your Twitter v2 developer account",
        required=True,
    )
    parser.add_argument(
        "--location",
        help="The location you would like to search listings for. Formats: city, state; latitude,longitude; or postal code",  # noqa: E501
        required=True,
    )
    parser.add_argument(
        "--distance",
        help="(Optional) Search for results within distance of location (in miles). Defaults to 25.",  # noqa: E501
        type=int,
        default=25,
        required=False,
    )
    parser.add_argument(
        "--twitter_account_name",
        help="(Optional) Twitter account name for the generated tweet. Used to construct a URL",  # noqa: E501
        required=False,
    )
    args = parser.parse_args()

    return {
        "petfinder_api_key": args.petfinder_api_key,
        "petfinder_secret": args.petfinder_secret,
        "twitter_api_key": args.twitter_api_key,
        "twitter_api_secret": args.twitter_api_secret,
        "twitter_access_token": args.twitter_access_token,
        "twitter_access_token_secret": args.twitter_access_token_secret,
        "twitter_account_name": args.twitter_account_name,
        "location": args.location,
        "distance": args.distance,
    }


def get_petfinder_oath_token(client_id: str, client_secret: str) -> str:
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(
        PETFINDER_TOKEN_URL,
        data=data,
    )
    response.raise_for_status()
    token = response.json().get("access_token")

    # Just in case an "access_token" isn't provided and the API
    # doesn't respond with the correct HTTP response code.
    if not (token and token.strip()):
        raise Exception("Petfinder OAuth token not included in response payload.")

    return token


def get_random_dog_listing(
    client_id: str, client_secret: str, location: str, distance: int
) -> dict:
    token = get_petfinder_oath_token(client_id, client_secret)
    headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}
    # https://www.petfinder.com/developers/v2/docs/#get-animals
    params = {
        "location": location,
        "distance": distance,
        "status": "adoptable",
        "type": "Dog",
        "sort": "random",
        "limit": 1,
    }
    response = requests.get(PETFINDER_API_URL, headers=headers, params=params)
    response.raise_for_status()
    results = response.json().get("animals")

    if not results:
        raise Exception(f"No dog listings found for {location}.")

    listing = results[0]

    if type(listing) is not dict:
        raise Exception("Listing is not a JSON object.")

    return listing


def validate_name(name: str) -> str:
    # Simple heuristic to catch some cases where the name might be updated
    # but the status of the listing hasn't been updated yet.
    if "adoption pending" in name.lower():
        raise Exception("Name indicates this dog is in the process of being adopted!")

    return name


def is_multiple(name: str) -> bool:
    return (
        name is not None
        and ("&" in name or " and " in name)
        and not ("-" in name or "~" in name or ("(" in name and ")" in name))
    )


def generate_tweet(listing: dict) -> str:
    name = validate_name(
        listing.get("name", f"This {random.choice(DEFAULT_NAMES)}").strip()
    )
    end_phrase = random.choice(
        MULTIPLE_END_PHRASES if is_multiple(name) else SINGLE_END_PHRASES
    )
    url = listing.get("url")

    if not url:
        raise Exception("No valid URL found.")

    return f"{name} {end_phrase} {url}"


def get_image_url(listing: dict) -> str | None:
    primary_images = listing.get("primary_photo_cropped", {})
    image_url = None

    # Find the largest image available
    for key in ["full", "large", "medium", "small"]:
        image_url = primary_images.get(key)
        if image_url is not None:
            break

    return image_url


def upload_image(
    listing: dict,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
) -> str | None:
    image_url = get_image_url(listing)

    if image_url is None:
        return

    image_req_res = requests.get(image_url)
    image_req_res.raise_for_status()

    # Create in-memory file object
    with io.BytesIO(image_req_res.content) as file:
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Use Twitter's v1 API because v2 doesn't support image uploads yet
        api = tweepy.API(auth)
        media = api.media_upload(
            "buddy.jpg",
            file=file,
        )

        # TODO: Can we fix the typing here? Would rather not ignore.
        return media.media_id  # type: ignore


def send_tweet(
    tweet_text: str,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
    tweet_media_id: int | str = None,
) -> str:
    if (media_ids := tweet_media_id) is not None:
        media_ids = [tweet_media_id]

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    response = client.create_tweet(text=tweet_text, media_ids=media_ids)

    # TODO: Can we fix the typing here? Would rather not ignore.
    return response.data.get("id")  # type: ignore


def main() -> None:
    cli_args = get_cli_args()
    tweet_id = None

    print("\n🐶 Finding a buddy!")
    try:
        for i in range(1, MAX_ATTEMPTS + 1):
            print(f"🐾 Tweet attempt #{i}...")

            try:
                listing = get_random_dog_listing(
                    cli_args["petfinder_api_key"],
                    cli_args["petfinder_secret"],
                    cli_args["location"],
                    cli_args["distance"],
                )
                tweet_text = generate_tweet(listing)
                tweet_media_id = upload_image(
                    listing,
                    cli_args["twitter_api_key"],
                    cli_args["twitter_api_secret"],
                    cli_args["twitter_access_token"],
                    cli_args["twitter_access_token_secret"],
                )
                tweet_id = send_tweet(
                    tweet_text,
                    cli_args["twitter_api_key"],
                    cli_args["twitter_api_secret"],
                    cli_args["twitter_access_token"],
                    cli_args["twitter_access_token_secret"],
                    tweet_media_id,
                )
            except Exception as e:
                print_indented(str(e))

                if i < MAX_ATTEMPTS:
                    continue

                raise e
            else:
                break
    except Exception:
        print("😿 Tweet could not be created:\n")
        print_indented(traceback.format_exc())
        sys.exit(1)
    else:
        success_msg = "🐦 Tweeted successfully!"

        if tweet_id and cli_args["twitter_account_name"] is not None:
            success_msg = f"{success_msg} https://twitter.com/{cli_args['twitter_account_name']}/status/{tweet_id}"  # noqa: E501

        print(success_msg)


if __name__ == "__main__":
    main()
