Find-A-Buddy
==========

[![Tweet a new buddy!](https://github.com/kaicataldo/findabuddy/actions/workflows/tweet.yml/badge.svg)](https://github.com/kaicataldo/findabuddy/actions/workflows/tweet.yml)
[![CI](https://github.com/kaicataldo/findabuddy/actions/workflows/ci.yml/badge.svg)](https://github.com/kaicataldo/findabuddy/actions/workflows/ci.yml)

      ,:'/  _ ..._         ______ _           _                    ____            _     _
     // ( `""-.._.'       |  ____(_)         | |        /\        |  _ \          | |   | |
     \| /    6\___        | |__   _ _ __   __| |______ /  \ ______| |_) |_   _  __| | __| |_   _
     |     6      4       |  __| | | '_ \ / _` |______/ /\ \______|  _ <| | | |/ _` |/ _` | | | |
     |            /       | |    | | | | | (_| |     / ____ \     | |_) | |_| | (_| | (_| | |_| |
     \_       .--'        |_|    |_|_| |_|\__,_|    /_/    \_\    |____/ \__,_|\__,_|\__,_|\__, |
     (_'---'`)                                                                              __/ |
                                                                                           |___/

Find-A-Buddy is a Twitter bot that uses the PetFinder API to tweet listings of adoptable dogs in a given geographic area. To create your own Find-A-Buddy Twitter bot, all you need is your own [Petfinder API key](https://www.petfinder.com/developers/api-key), your own [Twitter app auth credentials](https://apps.twitter.com/), and a process to invoke the script at a set interval.

This is a rewrite of one of my very first [projects](https://github.com/kaicataldo/findabuddy-v1), this time written in Python since it's the current language I'm learning 😊.

# DEPRECATION NOTICE
__Given the recent goings-on at Twitter (both from an organizational and technical view), I've decided to deprecate this repository. https://twitter.com/findabuddynyc suddenly stopped running with little warning due to breaking API changes (and now I can't even access the page any more because Twitter is currently not letting users view tweets unless they're logged in). It was a fun nearly 9 years (still can't believe I started this that long ago!), and thanks to all the Twitter users who supported the account along the way. 🐶❤️__

# Usage

This little script was written with the intention of making it easy for others to stand up their own local Find-A-Buddy Twitter account. The author is new to Python at the time this was written, so any input on improving this setup would be greatly appreciated!

You'll need to set up some sort of cron job that runs the script at a regular interval. Do be careful with this - Twitter has guidelines about what they think consitutes spam. Learn more about these guidelines [here](https://dev.twitter.com/overview/terms/policy).

## Running the script

1. Install [pipenv](https://pipenv.pypa.io/en/latest/).
1. Clone the repo into the execution environment.
1. Run `pipenv install` in the root directory of this repository.
1. Run `pipenv run python findabuddy` with the required options outlined below.

## Configuration

### Options

Find-A-Buddy accepts the following command line arguments:

```sh
  -h, --help            show this help message and exit
  --petfinder_api_key PETFINDER_API_KEY
                        Your key for the Petfinder API
  --petfinder_secret PETFINDER_SECRET
                        Your secret for the Petfinder API
  --twitter_api_key TWITTER_API_KEY
                        Your key for the Twitter v2 API
  --twitter_api_secret TWITTER_API_SECRET
                        Your secret for the Twitter v2 API
  --twitter_access_token TWITTER_ACCESS_TOKEN
                        Your access token for your Twitter v2 developer account
  --twitter_access_token_secret TWITTER_ACCESS_TOKEN_SECRET
                        Your access token secret for your Twitter v2 developer account
  --location LOCATION   The location you would like to search listings for. Formats: city, state; latitude,longitude; or postal code
  --distance DISTANCE   (Optional) Search for results within distance of location (in miles). Defaults to 25.
  --twitter_account_name TWITTER_ACCOUNT_NAME
                        (Optional) Twitter account name for the generated tweet. Used to construct a URL
```

### Example

```sh
pipenv run python findabuddy \
    --petfinder_api_key <Petfinder API key> \
    --petfinder_secret <Petfinder API secret> \
    --twitter_api_key <Twitter API key> \
    --twitter_api_secret <Twitter API secret> \
    --twitter_access_token <Twitter Developer account access token> \
    --twitter_access_token_secret <Twitter Developer account access token secret> \
    --location "New York, New York" \
    --distance 50 \
    --twitter_account_name "FindABuddyNYC"
```

# Dedication

This project is dedicated to [Henri](https://www.instagram.com/henrisnuggles/), who reminds you to please adopt instead of buying!
