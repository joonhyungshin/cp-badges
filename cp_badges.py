import os
from enum import Enum

from flask import Flask, abort, make_response
from flask_caching import Cache

import requests


config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

SHIELD_IO_BADGE_URL = os.getenv('SHIELD_IO_BADGE_URL', 'https://img.shields.io/badge')

CODEFORCES_API_URL = os.getenv('CODEFORCES_API_URL', 'https://codeforces.com/api/user.info')
CODEFORCES_PROFILE_URL = os.getenv('CODEFORCES_PROFILE_URL', 'https://codeforces.com/profile')
CODEFORCES_LOGO_B64 = os.getenv('CODEFORCES_LOGO_B64')

TOPCODER_API_URL = os.getenv('TOPCODER_API_URL', 'https://api.topcoder.com/v2/users')
TOPCODER_PROFILE_URL = os.getenv('TOPCODER_PROFILE_URL', 'https://www.topcoder.com/members/{handle}/details/'
                                                         '?track=DATA_SCIENCE&subTrack=SRM')
TOPCODER_LOGO_B64 = os.getenv('TOPCODER_LOGO_B64')

ATCODER_API_URL = os.getenv('ATCODER_API_URL', 'https://atcoder.jp/users/{handle}/history/json')
ATCODER_PROFILE_URL = os.getenv('ATCODER_PROFILE_URL', 'https://atcoder.jp/users')
ATCODER_LOGO_B64 = os.getenv('ATCODER_LOGO_B64')


class OJ(Enum):
    CODEFORCES = 1
    TOPCODER = 2
    ATCODER = 3


def get_cf_rating_and_color(handle):
    resp = requests.get(CODEFORCES_API_URL, params={'handles': handle})
    if not resp.ok:
        abort(404)
    data = resp.json()
    if data['status'] != 'OK':
        abort(404)
    user = data['result'][0]
    rank = user.get('rank')
    rating = user.get('rating')
    color_dict = {
        'legendary grandmaster': 'FF0000',
        'international grandmaster': 'FF0000',
        'grandmaster': 'FF0000',
        'international master': 'FF8C00',
        'master': 'FF8C00',
        'candidate master': 'AA00AA',
        'expert': '0000FF',
        'specialist': '03A89E',
        'pupil': '008000',
        'newbie': '808080',
    }
    color = color_dict.get(rank, 'black')
    rating = rating or 'unrated'
    return rating, color


def get_tc_rating_and_color(handle):
    resp = requests.get('{}/{}'.format(TOPCODER_API_URL, handle))
    if not resp.ok:
        abort(404)
    data = resp.json()
    if 'error' in data:
        abort(404)
    for rating_info in data.get('ratingSummary', []):
        if rating_info.get('name') == 'Algorithm':
            rating = rating_info['rating']
            color = rating_info['colorStyle'][-6:]
            break
    else:
        rating = 'unrated'
        color = 'black'
    return rating, color


def get_ac_rating_and_color(handle):
    resp = requests.get(ATCODER_API_URL.format(handle=handle))
    if not resp.ok:
        abort(404)
    data = resp.json()

    def _get_color(_rating):
        if _rating < 400:
            return '808080'
        elif _rating < 800:
            return '804000'
        elif _rating < 1200:
            return '008000'
        elif _rating < 1600:
            return '00C0C0'
        elif _rating < 2000:
            return '0000FF'
        elif _rating < 2400:
            return 'C0C000'
        elif _rating < 2800:
            return 'FF8000'
        else:
            return 'FF0000'

    if data:
        rating = data[-1]['NewRating']
        color = _get_color(rating)
    else:
        resp = requests.get('{}/{}'.format(ATCODER_PROFILE_URL, handle))
        if not resp.ok:
            abort(404)
        rating = 'unrated'
        color = 'black'
    return rating, color


@cache.memoize(300)
def get_rating_and_color(oj, handle):
    if oj == OJ.CODEFORCES:
        return get_cf_rating_and_color(handle)
    elif oj == OJ.TOPCODER:
        return get_tc_rating_and_color(handle)
    elif oj == OJ.ATCODER:
        return get_ac_rating_and_color(handle)
    return 'unknown', 'black'


@cache.memoize(86400)
def get_badge(rating, color, logo, label, link):
    params = {}
    if logo is not None:
        params['logo'] = logo
    if link is not None:
        params['link'] = link
    badge_url = '{}/{}-{}-{}'.format(SHIELD_IO_BADGE_URL, label, rating, color)
    svg_resp = requests.get(badge_url, params=params)
    return svg_resp.content


def make_badge(oj, handle):
    rating, color = get_rating_and_color(oj, handle)
    if oj == OJ.CODEFORCES:
        logo = CODEFORCES_LOGO_B64
        label = 'Codeforces'
        link = '{}/{}'.format(CODEFORCES_PROFILE_URL, handle)
    elif oj == OJ.TOPCODER:
        logo = TOPCODER_LOGO_B64
        label = 'TopCoder'
        link = TOPCODER_PROFILE_URL.format(handle=handle)
    elif oj == OJ.ATCODER:
        logo = ATCODER_LOGO_B64
        label = 'AtCoder'
        link = '{}/{}'.format(ATCODER_PROFILE_URL, handle)
    else:
        logo = None
        label = 'Unknown'
        link = None
    return get_badge(rating, color, logo, label, link)


@app.route('/codeforces/<handle>.svg')
def codeforces_badge(handle):
    response = make_response(make_badge(OJ.CODEFORCES, handle))
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/topcoder/<handle>.svg')
def topcoder_badge(handle):
    response = make_response(make_badge(OJ.TOPCODER, handle))
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/atcoder/<handle>.svg')
def atcoder_badge(handle):
    response = make_response(make_badge(OJ.ATCODER, handle))
    response.headers['Cache-Control'] = 'no-cache'
    return response
