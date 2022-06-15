import os
from enum import Enum

import requests
from pybadges import badge

from flask import Flask, abort, Response
from flask_caching import Cache


config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

CODEFORCES_URL = os.getenv('CODEFORCES_URL', 'https://codeforces.com/')
CODEFORCES_API_URL = os.getenv('CODEFORCES_API_URL', 'https://codeforces.com/api/user.info')
CODEFORCES_PROFILE_URL = os.getenv('CODEFORCES_PROFILE_URL', 'https://codeforces.com/profile')
CODEFORCES_LOGO_URL = os.getenv('CODEFORCES_LOGO_URL', 'https://codeforces.org/s/0/android-icon-192x192.png')

TOPCODER_URL = os.getenv('TOPCODER_URL', 'https://www.topcoder.com/community/competitive-programming/')
TOPCODER_API_URL = os.getenv('TOPCODER_API_URL', 'https://api.topcoder.com/v2/users')
TOPCODER_PROFILE_URL = os.getenv('TOPCODER_PROFILE_URL', 'https://www.topcoder.com/members/{handle}/details/'
                                                         '?track=DATA_SCIENCE&subTrack=SRM')
TOPCODER_LOGO_URL = os.getenv('TOPCODER_LOGO_URL', 'https://www.topcoder.com/i/favicon.ico')

ATCODER_URL = os.getenv('ATCODER_URL', 'https://atcoder.jp/')
ATCODER_API_URL = os.getenv('ATCODER_API_URL', 'https://atcoder.jp/users/{handle}/history/json')
ATCODER_PROFILE_URL = os.getenv('ATCODER_PROFILE_URL', 'https://atcoder.jp/users')
ATCODER_LOGO_URL = os.getenv('ATCODER_LOGO_URL', 'https://img.atcoder.jp/assets/favicon.png')


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


def make_badge(oj, handle):
    rating, color = get_rating_and_color(oj, handle)
    if oj == OJ.CODEFORCES:
        logo = CODEFORCES_LOGO_URL
        label = 'Codeforces'
        left_link = CODEFORCES_URL
        right_link = '{}/{}'.format(CODEFORCES_PROFILE_URL, handle)
    elif oj == OJ.TOPCODER:
        logo = TOPCODER_LOGO_URL
        label = 'TopCoder'
        left_link = TOPCODER_URL
        right_link = TOPCODER_PROFILE_URL.format(handle=handle)
    elif oj == OJ.ATCODER:
        logo = ATCODER_LOGO_URL
        label = 'AtCoder'
        left_link = ATCODER_URL
        right_link = '{}/{}'.format(ATCODER_PROFILE_URL, handle)
    else:
        logo = None
        label = 'Unknown'
        left_link = None
        right_link = None
    return badge(left_text=label, right_text=str(rating),
                 left_link=left_link, right_link=right_link,
                 right_color='#' + color,
                 logo=logo, embed_logo=True)


@app.route('/codeforces/<handle>.svg')
def codeforces_badge(handle):
    response = Response(make_badge(OJ.CODEFORCES, handle), mimetype='image/svg+xml')
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/topcoder/<handle>.svg')
def topcoder_badge(handle):
    response = Response(make_badge(OJ.TOPCODER, handle), mimetype='image/svg+xml')
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/atcoder/<handle>.svg')
def atcoder_badge(handle):
    response = Response(make_badge(OJ.ATCODER, handle), mimetype='image/svg+xml')
    response.headers['Cache-Control'] = 'no-cache'
    return response

