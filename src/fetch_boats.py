"""Read Van Isle Marina's public listings page and save a snapshot of the boats.

The live site reads the same page through netlify/functions/boats.mjs. This
snapshot is built into boats.html so the page still lists boats if that live
read ever fails. Run: python3 fetch_boats.py
"""
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

SRC = 'https://vanislemarina.com/listings/'
OUT = Path(__file__).with_name('boats-snapshot.json')


def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def parse(page):
    boats = []
    for card in page.split('<div class="wp_rtp_listing wp_rtp_listing_import">')[1:]:
        bid = re.search(r'boatId=(\d+)', card)
        title = re.search(r'class="boat-listing-titile">(.*?)</div>', card, re.S)
        if not (bid and title):
            continue
        status = re.search(r'color:\s*#CCC;">(.*?)</div>', card, re.S)
        img = re.search(r'background-image:url\((.*?)\)', card)
        length = re.search(r'wp_rtp_length">LENGTH<br>(.*?)</div>', card, re.S)
        year = re.search(r'wp_rtp_year">YEAR<br>(.*?)</div>', card, re.S)
        price = re.search(r'wp_rtp_price">(.*?)<br>', card, re.S)
        p = clean(price.group(1)) if price else ''
        digits = re.sub(r'[^\d]', '', p)
        boats.append({
            'id': bid.group(1),
            'title': clean(title.group(1)),
            'year': clean(year.group(1)) if year else '',
            'length': clean(length.group(1)) if length else '',
            'price': ('$' + format(int(digits), ',')) if digits else '',
            'status': clean(status.group(1)) if status else '',
            'image': img.group(1).strip('\'" ') if img else '',
            'url': 'https://vanislemarina.com/boat-listings/?boatId=' + bid.group(1),
        })
    return boats


if __name__ == '__main__':
    req = urllib.request.Request(SRC, headers={'User-Agent': 'AlexanderLangleySite/1.0 (boats list)'})
    page = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    boats = parse(page)
    if not boats:
        sys.exit('No boats found on the listings page; the page layout may have changed.')
    OUT.write_text(json.dumps(boats, indent=1, ensure_ascii=False))
    print(f'Saved {len(boats)} boats to {OUT.name}')
