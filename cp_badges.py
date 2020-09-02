import os
from enum import Enum

from flask import Flask, abort, redirect
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
CODEFORCES_LOGO_B64 = os.getenv('CODEFORCES_LOGO_B64')

TOPCODER_API_URL = os.getenv('TOPCODER_API_URL', 'https://api.topcoder.com/v2/users')
TOPCODER_LOGO_B64 = os.getenv('TOPCODER_LOGO_B64')

ATCODER_API_URL = os.getenv('ATCODER_API_URL', 'https://atcoder.jp/users/{handle}/history/json')
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


@app.route('/codeforces/<handle>')
def codeforces_badge(handle):
    rating, color = get_rating_and_color(OJ.CODEFORCES, handle)
    badge_url = '{}/Codeforces-{}-{}?logo={}'.format(SHIELD_IO_BADGE_URL, rating, color, CODEFORCES_LOGO_B64)
    return redirect(badge_url)


@app.route('/topcoder/<handle>')
def topcoder_badge(handle):
    rating, color = get_rating_and_color(OJ.TOPCODER, handle)
    badge_url = '{}/TopCoder-{}-{}?logo={}'.format(SHIELD_IO_BADGE_URL, rating, color, TOPCODER_LOGO_B64)
    return redirect(badge_url)


@app.route('/atcoder/<handle>')
def atcoder_badge(handle):
    rating, color = get_rating_and_color(OJ.ATCODER, handle)
    badge_url = '{}/AtCoder-{}-{}?logo={}'.format(SHIELD_IO_BADGE_URL, rating, color, ATCODER_LOGO_B64)
    return redirect(badge_url)
