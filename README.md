# Alexander Langley, yacht broker: website

The public site for Alexander Langley at Van Isle Marina, Sidney BC.
Hosted on Netlify from this repository; every push to `main` goes live.

## What's here
- `site/`: the finished website Netlify serves (home page, boats for sale, privacy, 404).
- `netlify/functions/boats.mjs`: reads Van Isle Marina's public listings page and serves it at `/api/boats`. The boats page uses it, so new boats, price changes and "Sale Pending" show up on their own (cached for an hour).
- `src/`: the sources. Edit these, then rebuild.

## Forms (Netlify Forms)
Each form arrives as its own list in Netlify (Project > Forms):
- `valuation`: free valuation requests, with up to three photos
- `boat-question`: "Ask me about her" on a boat for sale
- `boat-search`: "Tell me what you're after"
- `market-notes`: market notes signups (owners not ready to sell yet)

Every submission carries `lead_source` (ChatGPT ad, Facebook, Google, Website...) and the UTM tags of the ad that brought the visitor, and the email subject reads like `Valuation request: 2004 Grand Banks 42 Classic, 42 ft | ChatGPT ad`.

Tag ad links with UTM parameters, for example
`https://alexanderlangleyyachts.com/?utm_source=chatgpt&utm_medium=cpc&utm_campaign=valuation`.

## Rebuilding after a change
```
cd src && npm install        # once
python3 fetch_boats.py       # optional: refresh the fallback boat list
python3 build.py
```
Then commit and push.
