"""Builds the website into ../site from the sources in this folder.

Run from anywhere:  python3 src/build.py
Needs: npm install (in src/) once, for the icons.
Boat list fallback: python3 src/fetch_boats.py refreshes boats-snapshot.json.
"""
import re, os, html, json
from pathlib import Path
from urllib.parse import quote

SRC = Path(__file__).resolve().parent
REPO = SRC.parent
OUT = REPO / 'site'
ICONS = str(SRC / 'node_modules/@phosphor-icons/core/assets/regular') + '/'
SITE_URL = 'https://alexanderlangleyyachts.com'


def icon(name, cls='icon'):
    svg = open(ICONS + name + '.svg').read().strip()
    svg = svg.replace('<svg xmlns="http://www.w3.org/2000/svg"', f'<svg class="{cls}" aria-hidden="true" focusable="false"', 1)
    return svg


def icons_in(s):
    return re.sub(r'\{\{i:([a-z\-]+)\}\}', lambda m: icon(m.group(1)), s)


def mask(name):
    svg = open(ICONS + name + '.svg').read().strip()
    return 'url("data:image/svg+xml,' + quote(svg) + '")'


TEL = '<a class="tel" href="tel:+12505148944">250 514 8944</a>'
MAPS = 'https://www.google.com/maps/search/?api=1&amp;query=Van%20Isle%20Marina%2C%202320%20Harbour%20Road%2C%20Sidney%20BC'


# ---------- shared chrome ----------
def nav(page):
    home = 'index.html'
    cur = lambda p: ' aria-current="page"' if p == page else ''
    pre = '' if page == 'home' else home
    links = [
        ('home', home if page != 'home' else '#main', 'Sell your boat'),
        ('how', pre + '#how-it-works', 'How it works'),
        ('about', pre + '#about', 'About'),
        ('boats', 'boats.html', 'Boats for sale'),
    ]
    if page == 'boats':
        cta = '<a class="btn button-sm" href="#find" data-open="find">Find a boat</a>'
        cta_m = '<a class="btn button-md" href="#find" data-open="find">Tell me what you’re after' + icon('arrow-right') + '</a>'
    elif page == 'home':
        cta = '<a class="btn button-sm" href="#value" data-open="value">Free valuation</a>'
        cta_m = '<a class="btn button-md" href="#value" data-open="value">Get my free valuation' + icon('arrow-right') + '</a>'
    else:
        cta = '<a class="btn button-sm" href="index.html#value">Free valuation</a>'
        cta_m = '<a class="btn button-md" href="index.html#value">Get my free valuation' + icon('arrow-right') + '</a>'
    pill = '\n'.join(f'      <a class="title-4" href="{h}"{cur(k)}>{t}</a>' for k, h, t in links)
    menu = '\n'.join(f'      <li style="--i:{i}"><a class="heading-4" href="{h}"{cur(k)}>{t}</a></li>' for i, (k, h, t) in enumerate(links))
    return f'''<header>
  <nav class="nav" aria-label="Main">
    <a class="brand" href="{home if page != 'home' else '#main'}"><span class="title-3">Alexander Langley</span><small class="caption-5">Yacht broker, Van Isle Marina</small></a>
    <div class="nav-links">
{pill}
    </div>
    {cta}
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span></span><span></span><b class="sr caption-3">Menu</b></button>
  </nav>
  <div class="menu" id="menu" inert>
    <ul>
{menu}
    </ul>
    <div class="menu-foot">
      {cta_m}
      <p class="body-6 muted">Or call or text {TEL}</p>
    </div>
  </div>
</header>'''


def footer():
    return f'''<footer class="foot wrap" aria-label="Contact">
  <figure>
    <div class="photo">
      <picture>
        <source media="(max-width: 767px)" srcset="img/anchor-tall-1000.jpg">
        <img src="img/anchor-wide-2016.jpg" srcset="img/anchor-wide-1200.jpg 1200w, img/anchor-wide-2016.jpg 2016w" sizes="(min-width: 1280px) 1200px, 100vw" width="2016" height="864" loading="lazy" alt="Alexander’s 1978 CHB 34 trawler at anchor in a still, tree lined Gulf Islands cove at dusk">
      </picture>
    </div>
    <figcaption class="foot-cap caption-2">My 1978 CHB 34, at anchor in the Gulf Islands.</figcaption>
  </figure>
  <div class="foot-grid">
    <div class="stack-200">
      <h2 class="heading-4">Fair winds</h2>
      <p class="body-3 md:body-7">Selling, buying, or just wondering what she’s worth? I’m always happy to talk boats.</p>
    </div>
    <ul class="foot-lines">
      <li><small class="caption-2">Call or text</small><a class="title-2 tel" href="tel:+12505148944">250 514 8944</a></li>
      <li><small class="caption-2">Email</small><a class="title-2" href="mailto:alangley@vanislemarina.com">alangley@vanislemarina.com</a></li>
      <li><small class="caption-2">Office</small><a class="title-2" href="{MAPS}" target="_blank" rel="noopener">Van Isle Marina, 2320 Harbour Road, Sidney</a></li>
      <li><small class="caption-2">YouTube</small><a class="title-2" href="https://www.youtube.com/@alexanderlangleyyacht" target="_blank" rel="noopener">@alexanderlangleyyacht</a></li>
    </ul>
  </div>
  <div class="foot-base caption-2">
    <p>© 2026 Alexander Langley, yacht broker with Van Isle Marina, Sidney, British Columbia</p>
    <nav aria-label="Footer"><a href="index.html">Sell your boat</a><a href="boats.html">Boats for sale</a><a href="privacy.html">Privacy and terms</a></nav>
  </div>
</footer>'''


# ---------- FAQ ----------
FAQ = [
    ('What’s your commission?', 'A standard brokerage percentage of the selling price, plus GST, paid from the sale at closing. Nothing comes out of your pocket before then. Before you sign, I’ll show you in writing exactly what you’d net at your asking price.'),
    ('Can I keep using her while she’s listed?', 'Yes. Most owners keep boating until there’s an accepted offer. We plan showings around your trips.'),
    ('Do I have to fix things before listing?', 'Usually not. I’ll point out the few things worth doing because buyers and surveyors will notice them, and tell you what isn’t worth the money.'),
    ('What if I change my mind?', 'Until you sign a listing agreement, you can stop at any point and it costs you nothing. The agreement itself explains how it can be ended, and I go through that with you before you sign.'),
    ('Is now a good time to sell?', 'It depends on your boat. Spring is when most buyers on the Island are looking, so many owners get ready over the winter. Your valuation will show where your boat sits in today’s market.'),
    ('How long will it take to sell?', 'It depends on the boat, the price and the season. Realistically priced boats sell fastest, and spring and early summer are the busiest months here. Your valuation includes my honest view on timing.'),
    ('Does my boat have to be at Van Isle?', 'No. I sell boats wherever they’re kept on Vancouver Island and in the Gulf Islands.'),
    ('Do I need to be there for showings?', 'No. I show the boat and answer buyers’ questions, and once there’s an accepted offer I run the sea trial. You’re welcome to come along whenever you’d like to.'),
    ('Can I sell a boat that still has a loan on it?', 'Yes. The loan is paid out from the sale at closing, and I coordinate that with your lender.'),
    ('Do you sell sailboats too?', 'Yes. I sell power and sail, all brands.'),
    ('Do you handle boathouses?', 'Yes. I help owners sell their boathouses, and help buyers find and buy one.'),
    ('I’m buying another boat too. Can you help with both?', 'Yes. I can sell your boat and help you find the next one, and Van Isle Marina has a trade program for owners who are changing boats. Ask me how it would work for you.'),
    ('What do you need from me to get started?', 'Just the answers to six short questions. Her service records and any past survey help, but you don’t need them for the valuation.'),
]
FAQ_HTML = '\n'.join(f'        <details><summary class="title-2">{q}{icon("plus")}</summary><p class="body-3 md:body-7">{a}</p></details>' for q, a in FAQ)


# ---------- client quotes ----------
# Add real quotes as (quote, "First name, boat") to show the section. Empty list hides it.
QUOTES = []
QUOTES_HTML = ('    <div class="quotes">\n      <h3 class="heading-5" data-reveal>What clients say</h3>\n' + '\n'.join(
    f'      <figure class="quote" data-reveal><blockquote class="body-7 ph">{q}</blockquote><figcaption class="caption-2">{who}</figcaption></figure>' for q, who in QUOTES) + '\n    </div>\n') if QUOTES else ''


# ---------- chart decorations ----------
CHART_DECO = '''<svg class="chart-deco deco-isle-a" viewBox="0 0 400 300" aria-hidden="true">
        <path d="M400 262 C 360 290, 304 280, 274 252 C 248 230, 220 232, 192 212 C 154 186, 166 144, 140 124 C 110 100, 112 48, 140 14 C 146 8, 150 4, 154 0" fill="none" stroke="var(--chart-contour)" stroke-width="1.5" stroke-dasharray="1 6" stroke-linecap="round"/>
        <path d="M400 236 C 366 262, 318 254, 290 228 C 266 206, 236 208, 210 190 C 176 166, 190 128, 164 108 C 136 86, 142 40, 170 16 C 180 8, 190 2, 196 0" fill="none" stroke="var(--chart-contour)" stroke-width="1.5"/>
        <path d="M400 0 L400 210 C 372 236, 330 228, 304 204 C 280 182, 250 186, 226 168 C 196 146, 214 112, 186 92 C 160 72, 168 34, 196 18 C 214 8, 230 0, 240 0 Z" fill="var(--chart-land)" stroke="var(--chart-land-edge)" stroke-width="1.5"/>
        <ellipse cx="146" cy="232" rx="11" ry="7" fill="var(--chart-land)" stroke="var(--chart-land-edge)" stroke-width="1.5"/>
      </svg>
      <svg class="chart-deco deco-isle-c" viewBox="0 0 220 200" aria-hidden="true">
        <path d="M220 18 C 186 12, 148 34, 138 70 C 128 104, 146 128, 136 152 C 128 176, 166 196, 220 192" fill="none" stroke="var(--chart-contour)" stroke-width="1.5"/>
        <path d="M220 40 C 196 36, 168 52, 160 78 C 152 104, 170 128, 160 150 C 154 166, 176 176, 220 170 Z" fill="var(--chart-land)" stroke="var(--chart-land-edge)" stroke-width="1.5"/>
      </svg>
      <svg class="chart-deco deco-isle-b" viewBox="0 0 360 260" aria-hidden="true">
        <path d="M0 8 C 42 -6, 98 8, 128 40 C 152 66, 186 62, 216 90 C 252 124, 238 168, 270 192 C 292 210, 308 232, 316 260" fill="none" stroke="var(--chart-contour)" stroke-width="1.5" stroke-dasharray="1 6" stroke-linecap="round"/>
        <path d="M0 34 C 36 20, 84 34, 110 62 C 134 88, 168 84, 196 110 C 228 140, 214 182, 246 206 C 266 222, 280 240, 286 260" fill="none" stroke="var(--chart-contour)" stroke-width="1.5"/>
        <path d="M0 60 C 30 48, 70 60, 92 84 C 116 110, 150 104, 176 128 C 204 154, 190 196, 222 220 C 240 234, 252 248, 256 260 L0 260 Z" fill="var(--chart-land)" stroke="var(--chart-land-edge)" stroke-width="1.5"/>
        <circle cx="302" cy="148" r="8" fill="var(--chart-land)" stroke="var(--chart-land-edge)" stroke-width="1.5"/>
      </svg>
      <svg class="chart-deco deco-rose" viewBox="0 -14 100 114" aria-hidden="true">
        <circle cx="50" cy="50" r="44" fill="none" stroke="currentColor" stroke-width="1"/>
        <circle cx="50" cy="50" r="36" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="1 4"/>
        <path d="M50 8 L56 44 L92 50 L56 56 L50 92 L44 56 L8 50 L44 44 Z" fill="none" stroke="currentColor" stroke-width="1" stroke-linejoin="round"/>
        <path d="M50 8 L56 44 L50 50 Z M92 50 L56 56 L50 50 Z M50 92 L44 56 L50 50 Z M8 50 L44 44 L50 50 Z" fill="currentColor"/>
        <text x="50" y="-3" text-anchor="middle" class="caption-3" fill="currentColor">N</text>
      </svg>'''


# ---------- Netlify form plumbing ----------
def NF(name, extra=''):
    fields = ['form-name', 'subject', 'lead_source', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'landing_page', 'referrer']
    rows = '\n'.join(f'    <input type="hidden" name="{f}" value="{name if f == "form-name" else ""}">' for f in fields)
    return rows + extra + '\n    <p class="sr" aria-hidden="true"><label>Leave this empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>'


# ---------- step-through forms ----------
ARROW = icon('arrow-right')
CLOSE = icon('x')


def opts(name, items, small=False, stay=False):
    rows = []
    for it in items:
        val, label = (it, it) if isinstance(it, str) else it
        ic = '' if stay else ARROW
        rows.append(f'            <label class="opt"><input type="radio" name="{name}" value="{val}"><span class="{"body-3" if small else "title-2"}">{label}</span>{ic}</label>')
    cls = 'opts small' if small else 'opts'
    attrs = ' data-stay' if stay else ''
    return f'          <div class="{cls}"{attrs}>\n' + '\n'.join(rows) + '\n          </div>'


BACK = '          <div class="step-actions"><button type="button" class="back button-md" data-back>Back</button></div>'
def nextback(): return '          <div class="step-actions"><button type="button" class="btn button-md" data-next>Continue' + ARROW + '</button><button type="button" class="back button-md" data-back>Back</button></div>'
Q = 'q heading-5 md:heading-3'


def contact(p, legend, note=False, consent='Alexander can contact me about my boat. I can opt out at any time.', help='An email address or a phone number is enough, whichever suits you.'):
    extra = (f'            <div class="field"><label class="title-4" for="{p}-note">How will you use her? (optional)</label><textarea id="{p}-note" name="note" rows="3" placeholder="Weekends in the Gulf Islands with the grandkids"></textarea></div>\n' if note else '')
    return f'''        <fieldset class="step" data-step="contact" hidden>
          <legend class="{Q}" tabindex="-1">{legend}</legend>
          <p class="q-help body-3">{help}</p>
          <div class="fields">
            <div class="field"><label class="title-4" for="{p}-name">Your name</label><input id="{p}-name" name="name" autocomplete="name" aria-describedby="{p}-e-contact"></div>
            <div class="field"><label class="title-4" for="{p}-email">Email</label><input id="{p}-email" name="email" type="email" autocomplete="email" inputmode="email" aria-describedby="{p}-e-contact"></div>
            <div class="field"><label class="title-4" for="{p}-phone">Phone</label><input id="{p}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" aria-describedby="{p}-e-contact"></div>
{extra}            <div class="field" role="radiogroup" aria-labelledby="{p}-how-l"><span class="legend title-4" id="{p}-how-l">How would you like to hear from me?</span>
{opts('reply_by', [('email', 'By email'), ('call', 'A phone call first, I’d rather talk'), ('text', 'A text message')], small=True, stay=True)}
            </div>
            <label class="check body-6"><input type="checkbox" id="{p}-consent" name="consent" value="yes" aria-describedby="{p}-e-contact"><span>{consent}</span></label>
            <p class="err body-5" id="{p}-e-contact" hidden></p>
          </div>
          <div class="step-actions"><button type="submit" class="btn button-md">Send my request{ARROW}</button><button type="button" class="back button-md" data-back>Back</button></div>
        </fieldset>'''


def done(sentence):
    return f'''        <div class="step" data-step="done" hidden>
          <h2 class="{Q}" tabindex="-1">Thanks, <span data-out="first">there</span></h2>
          <p class="done-sum body-3 md:body-7">{sentence} You’ll hear from me within one business day. </p>
          <div class="step-actions"><button type="button" class="btn button-md" data-close>Back to the site</button></div>
        </div>'''


def dialog(id_, title, close_label, first_q_id, steps, aside, form_name, extra=''):
    return f'''<dialog class="val" id="{id_}" aria-labelledby="{first_q_id}">
  <form class="val-form" name="{form_name}" method="POST" data-netlify="true" data-netlify-honeypot="bot-field" novalidate>
{NF(form_name, extra)}
    <div class="val-top">
      <p class="title-3">{title}</p>
      <button type="button" class="icon-btn" data-close aria-label="{close_label}">{CLOSE}</button>
    </div>
    <div class="val-bar" aria-hidden="true"><span></span></div>
    <div class="val-body">
      <div class="val-main">
{steps}
      </div>
{aside}
    </div>
  </form>
</dialog>'''


V_STEPS = '\n\n'.join([
f'''        <fieldset class="step" data-step="type">
          <legend class="{Q}" id="q-type" tabindex="-1">What kind of boat is she?</legend>
{opts('type', ['Motor yacht or cruiser', 'Trawler', 'Sportfish or centre console', 'Sailboat', 'Something else'])}
        </fieldset>''',
f'''        <fieldset class="step" data-step="model" hidden>
          <legend class="{Q}" tabindex="-1">Make, model and year</legend>
          <p class="q-help body-3">Whatever is on her papers is fine. Leave the model blank if you’re not sure.</p>
          <div class="fields">
            <div class="field"><label class="title-4" for="v-make">Make</label><input id="v-make" name="make" autocomplete="off" placeholder="Grand Banks" aria-describedby="v-e-model"></div>
            <div class="row2">
              <div class="field"><label class="title-4" for="v-model">Model</label><input id="v-model" name="model" autocomplete="off" placeholder="42 Classic"></div>
              <div class="field"><label class="title-4" for="v-year">Year</label><input id="v-year" name="year" inputmode="numeric" autocomplete="off" maxlength="4" placeholder="1998" aria-describedby="v-e-model"></div>
            </div>
            <p class="err body-5" id="v-e-model" hidden></p>
            <div class="field">
              <span class="title-4" id="v-photo-l">Up to three photos of her (optional)</span>
              <input class="sr" id="v-photo" type="file" accept="image/*" multiple aria-labelledby="v-photo-l" aria-describedby="v-e-photo">
              <label class="file button-md" for="v-photo">{icon('camera')}Add photos</label>
              <ul class="thumbs" data-thumbs aria-label="Photos you added"></ul>
              <p class="err body-5" id="v-e-photo" hidden></p>
              <input type="file" name="photo1" hidden><input type="file" name="photo2" hidden><input type="file" name="photo3" hidden>
            </div>
          </div>
{nextback()}
        </fieldset>''',
f'''        <fieldset class="step" data-step="length" hidden>
          <legend class="{Q}" tabindex="-1">How long is she, in feet?</legend>
          <p class="q-help body-3">As on her papers or listing. Half feet are fine, for example 34.5.</p>
          <div class="fields">
            <div class="field"><label class="title-4" for="v-len">Length</label><div class="feet"><input id="v-len" name="length" inputmode="decimal" autocomplete="off" placeholder="34" aria-describedby="v-e-len"><span class="body-3">feet</span></div></div>
            <p class="err body-5" id="v-e-len" hidden></p>
          </div>
{nextback()}
        </fieldset>''',
f'''        <fieldset class="step" data-step="place" hidden>
          <legend class="{Q}" tabindex="-1">Where is she kept?</legend>
{opts('place', [('Sidney and Saanich', 'Sidney or the Saanich Peninsula'), 'Victoria', 'Gulf Islands', 'Nanaimo to Ladysmith', 'Comox Valley and north', 'Mainland or the US'])}
{BACK}
        </fieldset>''',
f'''        <fieldset class="step" data-step="when" hidden>
          <legend class="{Q}" tabindex="-1">Are you thinking of selling?</legend>
{opts('when', [('This spring', 'Yes, this spring'), ('Within the year', 'Probably, within the year'), ('Just curious', 'Not sure, just curious for now')])}
{BACK}
        </fieldset>''',
contact('v', 'Where should I send it?'),
done('I’ll look at recent sales of boats like yours and <span data-out="next">be in touch</span>.'),
])

V_ASIDE = '''      <aside class="val-aside" aria-label="Your boat so far">
        <div class="vc">
          <div class="vc-photo" data-vc-photo hidden><img alt="Your photo of your boat"></div>
          <p class="vc-label caption-4">Your boat</p>
          <p class="vc-title heading-6" data-out="title">Not named yet</p>
          <dl class="vc-rows body-6">
            <div><dt>Type</dt><dd data-out="type">Not yet</dd></div>
            <div><dt>Length</dt><dd data-out="length">Not yet</dd></div>
            <div><dt>Kept at</dt><dd data-out="place">Not yet</dd></div>
            <div><dt>Selling</dt><dd data-out="when">Not yet</dd></div>
          </dl>
          <p class="vc-foot caption-5">Valuation by Alexander Langley, Van Isle Marina</p>
        </div>
        <p class="caption-2">Your answers stay between you and me.</p>
      </aside>'''

F_STEPS = '\n\n'.join([
f'''        <fieldset class="step" data-step="want">
          <legend class="{Q}" id="q-want" tabindex="-1">What are you looking for?</legend>
{opts('want', ['Motor yacht or cruiser', 'Trawler', 'Sportfish or centre console', 'Sailboat', 'Not sure yet'])}
        </fieldset>''',
f'''        <fieldset class="step" data-step="size" hidden>
          <legend class="{Q}" tabindex="-1">What length, in feet?</legend>
          <p class="q-help body-3">Leave one box empty if you’re flexible.</p>
          <div class="fields">
            <div class="range">
              <div class="field"><label class="title-4" for="f-from">From</label><div class="feet"><input id="f-from" name="from" inputmode="decimal" autocomplete="off" placeholder="34" aria-describedby="f-e-size"><span class="body-3">feet</span></div></div>
              <div class="field"><label class="title-4" for="f-to">To</label><div class="feet"><input id="f-to" name="to" inputmode="decimal" autocomplete="off" placeholder="42" aria-describedby="f-e-size"><span class="body-3">feet</span></div></div>
            </div>
            <p class="err body-5" id="f-e-size" hidden></p>
          </div>
{nextback()}
        </fieldset>''',
f'''        <fieldset class="step" data-step="budget" hidden>
          <legend class="{Q}" tabindex="-1">What’s your budget?</legend>
{opts('budget', ['Under $100,000', '$100,000 to $250,000', '$250,000 to $500,000', '$500,000 to $1 million', 'Over $1 million'])}
{BACK}
        </fieldset>''',
f'''        <fieldset class="step" data-step="soon" hidden>
          <legend class="{Q}" tabindex="-1">When would you like to be on the water?</legend>
{opts('soon', ['This season', 'Within the year', ('Just looking', 'Just looking for now')])}
{BACK}
        </fieldset>''',
contact('f', 'Where should I send boats?', note=True, consent='Alexander can contact me about boats for sale. I can opt out at any time.'),
done('I’ll go through what’s on the market and <span data-out="next">be in touch</span>.'),
])

F_ASIDE = '''      <aside class="val-aside" aria-label="Your search so far">
        <div class="vc">
          <p class="vc-label caption-4">Your next boat</p>
          <p class="vc-title heading-6" data-out="want">Still deciding</p>
          <dl class="vc-rows body-6">
            <div><dt>Length</dt><dd data-out="size">Not yet</dd></div>
            <div><dt>Budget</dt><dd data-out="budget">Not yet</dd></div>
            <div><dt>On the water</dt><dd data-out="soon">Not yet</dd></div>
          </dl>
          <p class="vc-foot caption-5">Search by Alexander Langley, Van Isle Marina</p>
        </div>
        <p class="caption-2">I look at boats from every brokerage on the coast, not only Van Isle’s.</p>
      </aside>'''

A_STEPS = '\n\n'.join([
    contact('a', 'Ask me about her', consent='Alexander can contact me about this boat. I can opt out at any time.', help='Is she still available, can you see her this week, what’s her history? Ask anything, and leave an email or a phone number.')
      .replace('<fieldset class="step" data-step="contact" hidden>', '<fieldset class="step" data-step="contact">')
      .replace(f'<legend class="{Q}" tabindex="-1">Ask me about her</legend>', f'<legend class="{Q}" id="q-ask" tabindex="-1">Ask me about her</legend>')
      .replace('<div class="field"><label class="title-4" for="a-phone">', '<div class="field"><label class="title-4" for="a-msg">Your question</label><textarea id="a-msg" name="message" rows="3"></textarea></div>\n            <div class="field"><label class="title-4" for="a-phone">'),
    done('I’ll look into her and <span data-out="next">be in touch</span>.'),
])
A_ASIDE = '''      <aside class="val-aside" aria-label="The boat you’re asking about">
        <div class="vc">
          <p class="vc-label caption-4">You’re asking about</p>
          <p class="vc-title heading-6" data-out="boat">This boat</p>
          <dl class="vc-rows body-6">
            <div><dt>Asking price</dt><dd data-out="price">Not yet</dd></div>
          </dl>
          <p class="vc-foot caption-5">Listed at Van Isle Marina</p>
        </div>
        <p class="caption-2">I can usually arrange a viewing within a few days.</p>
      </aside>'''

D_VALUE = dialog('value', 'Free boat valuation', 'Close valuation', 'q-type', V_STEPS, V_ASIDE, 'valuation')
D_FIND = dialog('find', 'Find a boat', 'Close boat search', 'q-want', F_STEPS, F_ASIDE, 'boat-search')
D_ASK = dialog('ask', 'Ask about a boat', 'Close question', 'q-ask', A_STEPS, A_ASIDE, 'boat-question',
               '\n    <input type="hidden" name="boat" value="">\n    <input type="hidden" name="asking_price" value="">\n    <input type="hidden" name="listing_url" value="">')


# ---------- boats ----------
SNAP = json.loads((SRC / 'boats-snapshot.json').read_text())
E = lambda v: html.escape(str(v or ''), quote=True)


def boat_bits(b):
    name = f"{b.get('year', '')} {b.get('title', '')}".strip()
    price = b.get('price') or 'Call for price'
    status = '' if (b.get('status') or 'Active').lower() == 'active' else b['status']
    return name, price, status


BOAT_IMGS = '\n'.join(f'        <img data-boat-img="{i}" src="{E(b["image"])}" width="1200" height="800" {"fetchpriority=\"high\"" if i == 0 else "loading=\"lazy\""} referrerpolicy="no-referrer" alt="{E(boat_bits(b)[0])}"{" class=\"is-on\"" if i == 0 else ""}>' for i, b in enumerate(SNAP))
BOAT_ROWS = '\n'.join(f'''          <li class="boat{" is-on" if i == 0 else ""}" data-i="{i}"><span class="boat-name title-2">{E(n)}</span><span class="boat-price title-2">{E(p)}</span><span class="boat-spec body-6">{E(b.get("length"))}{f' <span class="tag caption-4">{E(st)}</span>' if st else ''}</span><span class="boat-act"><button type="button" class="link-btn button-sm" data-ask="{E(n)}" data-price="{E(p)}" data-url="{E(b["url"])}">Ask me about her</button><a class="body-5" href="{E(b["url"])}" target="_blank" rel="noopener">Full listing and photos</a></span></li>''' for i, b in enumerate(SNAP) for (n, p, st) in [boat_bits(b)])


# ---------- assemble ----------
css = (SRC / 'style.css').read_text()
css += '\n:root{--warn:' + mask('warning-circle') + ';--tick:' + mask('check-circle') + '}\n'
js = (SRC / 'site.js').read_text()

# ChatGPT Ads measurement pixel. Paste the Pixel ID from Ads Manager > Tools > Conversions.
# Leave empty and no OpenAI script loads at all.
OAIQ_PIXEL_ID = '63VidfamjuhXsY4YjzUGtC'

def oaiq_tag():
    if not OAIQ_PIXEL_ID:
        return ''
    return ('<script>(function(w,d,s,u){if(w.oaiq)return;var q=function(){q.q.push(arguments)};q.q=[];w.oaiq=q;'
            'var js=d.createElement(s);js.async=true;js.src=u;var f=d.getElementsByTagName(s)[0];f.parentNode.insertBefore(js,f);'
            '})(window,document,"script","https://bzrcdn.openai.com/sdk/oaiq.min.js");'
            'oaiq("init",{pixelId:"%s"});</script>\n' % OAIQ_PIXEL_ID)

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/img/hero-trawler-1200.jpg">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{robots}{pixel}</head>
<body>
'''
TAIL = '\n</body>\n</html>\n'


def fill(s, extra):
    for k, v in extra.items():
        assert k in s, k
        s = s.replace(k, v)
    s = icons_in(s)
    s = re.sub(r'\{\{NF:([a-z\-]+)\}\}', lambda m: NF(m.group(1)), s)
    assert '{{' not in s, re.findall(r'\{\{[^}]+\}\}', s)[:5]
    return s


def absolute(s):
    s = re.sub(r'(src="|srcset="|, )(img|fonts)/', r'\1/\2/', s)
    s = s.replace('url("fonts/', 'url("/fonts/')
    s = s.replace('href="index.html#', 'href="/#').replace('href="index.html"', 'href="/"')
    s = s.replace('href="boats.html"', 'href="/boats"').replace('href="privacy.html"', 'href="/privacy"')
    return s


def page(name, body, title, desc, path, robots=''):
    doc = HEAD.format(title=title, desc=desc, url=SITE_URL + path, site=SITE_URL, robots=robots, pixel=oaiq_tag()) + absolute(body) + TAIL
    (OUT / name).write_text(doc)
    return doc


common = {'{{CSS}}': css, '{{FOOTER}}': footer(), '{{JS}}': js}
index = fill((SRC / 'index.src.html').read_text().replace('<title>Alexander Langley, Yacht Broker</title>\n', '', 1), {
    **common, '{{NAV:home}}': nav('home'), '{{FAQ}}': FAQ_HTML, '{{CHART_DECO}}': CHART_DECO, '{{QUOTES}}': QUOTES_HTML, '{{DIALOG_VALUE}}': D_VALUE})
boats = fill((SRC / 'boats.src.html').read_text(), {
    **common, '{{NAV:boats}}': nav('boats'), '{{BOAT_IMGS}}': BOAT_IMGS, '{{BOAT_ROWS}}': BOAT_ROWS, '{{DIALOGS}}': D_FIND + '\n\n' + D_ASK})
priv = fill((SRC / 'privacy.src.html').read_text(), {**common, '{{NAV:privacy}}': nav('privacy')})
lost = fill((SRC / 'notfound.src.html').read_text(), {**common, '{{NAV:other}}': nav('other')})

docs = [
    page('index.html', index, 'Sell your boat on Vancouver Island | Alexander Langley, Van Isle Marina',
         'Find out what your boat is worth with a free written valuation from Alexander Langley, yacht broker at Van Isle Marina in Sidney. Free, and nothing to sign.', '/'),
    page('boats.html', boats, 'Boats for sale at Van Isle Marina | Alexander Langley',
         'Every boat listed at Van Isle Marina in Sidney, BC, kept up to date, plus a free boat search from yacht broker Alexander Langley.', '/boats'),
    page('privacy.html', priv, 'Privacy and terms | Alexander Langley', 'How Alexander Langley handles the information you send through this site.', '/privacy',
         '<meta name="robots" content="noindex">\n'),
    page('404.html', lost, 'Page not found | Alexander Langley', 'This page isn’t here.', '/404', '<meta name="robots" content="noindex">\n'),
]
(OUT / 'favicon.svg').write_text((SRC / 'favicon.svg').read_text())
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{SITE_URL}{u}</loc></url>\n' for u in ['/', '/boats']) + '</urlset>\n')

used = set(re.findall(r'/img/([a-z0-9\-]+\.jpg)', ''.join(docs)))
missing = [f for f in used if not (OUT / 'img' / f).exists()]
assert not missing, missing
for f in (OUT / 'img').iterdir():
    if f.name not in used:
        f.unlink()
print('built', ', '.join(f'{n}' for n in ['index', 'boats', 'privacy', '404']), '| images', len(used), '| boats in fallback', len(SNAP))
