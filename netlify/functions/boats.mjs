// Live list of boats for sale, read from Van Isle Marina's public listings page.
// Served at /api/boats. Netlify's CDN keeps each answer for an hour, so Van Isle's
// site is asked at most about once an hour, and visitors always get a quick reply.

const SRC = 'https://vanislemarina.com/listings/';

const decode = (s) => s
  .replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#0?39;|&#8217;|&rsquo;/g, '’')
  .replace(/&#8211;|&ndash;/g, '–').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
const clean = (s) => decode(String(s || '').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const pick = (card, re) => { const m = card.match(re); return m ? m[1] : ''; };

export function parse(page) {
  const boats = [];
  for (const card of page.split('<div class="wp_rtp_listing wp_rtp_listing_import">').slice(1)) {
    const id = pick(card, /boatId=(\d+)/);
    const title = clean(pick(card, /class="boat-listing-titile">([\s\S]*?)<\/div>/));
    if (!id || !title) continue;
    const digits = clean(pick(card, /wp_rtp_price">([\s\S]*?)<br>/)).replace(/[^\d]/g, '');
    boats.push({
      id,
      title,
      year: clean(pick(card, /wp_rtp_year">YEAR<br>([\s\S]*?)<\/div>/)),
      length: clean(pick(card, /wp_rtp_length">LENGTH<br>([\s\S]*?)<\/div>/)),
      price: digits ? '$' + Number(digits).toLocaleString('en-CA') : '',
      status: clean(pick(card, /color:\s*#CCC;">([\s\S]*?)<\/div>/)),
      image: pick(card, /background-image:url\(([^)]*)\)/).replace(/^['"\s]+|['"\s]+$/g, ''),
      url: 'https://vanislemarina.com/boat-listings/?boatId=' + id,
    });
  }
  return boats;
}

export default async () => {
  try {
    const res = await fetch(SRC, { headers: { 'user-agent': 'AlexanderLangleySite/1.0 (boats list)' } });
    if (!res.ok) throw new Error('listings page answered ' + res.status);
    const boats = parse(await res.text());
    if (!boats.length) throw new Error('no boats found on the listings page');
    return Response.json({ updated: new Date().toISOString(), source: SRC, boats }, {
      headers: {
        'Cache-Control': 'public, max-age=300',
        'Netlify-CDN-Cache-Control': 'public, durable, s-maxage=3600, stale-while-revalidate=86400',
      },
    });
  } catch (err) {
    return Response.json({ error: String(err && err.message || err) }, {
      status: 502,
      headers: { 'Cache-Control': 'no-store' },
    });
  }
};

export const config = { path: '/api/boats' };
