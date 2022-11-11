import os
from enum import Enum

import requests
from pybadges import badge

from flask import Flask, abort, redirect, request, Response
from flask_caching import Cache


CACHE_TIMEOUT = os.getenv('CACHE_TIMEOUT', 300)


config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': CACHE_TIMEOUT
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


class Platform:
    @classmethod
    def get_profile_url(cls, handle):
        return cls.PROFILE_URL.format(handle=handle)

    @classmethod
    def get_rating_and_color(cls, handle):
        raise NotImplementedError

    @classmethod
    def make_badge(cls, handle):
        rating, color = cls.get_rating_and_color(handle)
        badge_args = {
            'left_text': cls.LABEL,
            'right_text': str(rating),
            'left_link': cls.URL,
            'right_link': cls.get_profile_url(handle),
            'logo': cls.LOGO_URL,
            'left_color': '#555',
            'right_color': color,
            'embed_logo': True,
        }
        customizable = [
            'left_text',
            'right_text',
            'left_link',
            'right_link',
            'whole_link',
            'logo',
            'left_color',
            'right_color',
            'whole_title',
            'left_title',
            'right_title',
            'id_suffix',
        ]
        for arg in customizable:
            if arg in request.args:
                badge_args[arg] = request.args.get(arg)
        try:
            return badge(**badge_args)
        except ValueError:
            abort(400)

    @classmethod
    def make_response(cls, handle):
        response = Response(cls.make_badge(handle), mimetype='image/svg+xml')
        response.cache_control.max_age = CACHE_TIMEOUT
        return response


class Codeforces(Platform):
    LABEL = 'Codeforces'
    URL = 'https://codeforces.com/'
    API_URL = 'https://codeforces.com/api/user.info'
    PROFILE_URL = 'https://codeforces.com/profile/{handle}'
    LOGO_URL = 'https://codeforces.org/s/0/android-icon-192x192.png'

    @classmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_rating_and_color(cls, handle):
        resp = requests.get(cls.API_URL, params={'handles': handle})
        if not resp.ok:
            abort(404)
        data = resp.json()
        if data['status'] != 'OK':
            abort(404)
        user = data['result'][0]
        rank = user.get('rank')
        rating = user.get('rating')
        color_dict = {
            'legendary grandmaster': '#FF0000',
            'international grandmaster': '#FF0000',
            'grandmaster': '#FF0000',
            'international master': '#FF8C00',
            'master': '#FF8C00',
            'candidate master': '#AA00AA',
            'expert': '#0000FF',
            'specialist': '#03A89E',
            'pupil': '#008000',
            'newbie': '#808080',
        }
        color = color_dict.get(rank, 'black')
        rating = rating or 'unrated'
        return rating, color


class TopCoder(Platform):
    LABEL = 'TopCoder'
    URL = 'https://www.topcoder.com/community/competitive-programming/'
    API_URL = 'https://api.topcoder.com/v2/users'
    PROFILE_URL = 'https://www.topcoder.com/members/{handle}'
    LOGO_URL = 'https://www.topcoder.com/i/favicon.ico'

    @classmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_rating_and_color(cls, handle):
        resp = requests.get('{}/{}'.format(cls.API_URL, handle))
        if not resp.ok:
            abort(404)
        data = resp.json()
        if 'error' in data:
            abort(404)
        for rating_info in data.get('ratingSummary', []):
            if rating_info.get('name') == 'Algorithm':
                rating = rating_info['rating']
                color = '#' + rating_info['colorStyle'][-6:]
                break
        else:
            rating = 'unrated'
            color = 'black'
        return rating, color


class AtCoder(Platform):
    LABEL = 'AtCoder'
    URL = 'https://atcoder.jp/'
    API_URL = 'https://atcoder.jp/users/{handle}/history/json'
    PROFILE_URL = 'https://atcoder.jp/users'
    LOGO_URL = 'https://img.atcoder.jp/assets/favicon.png'

    @classmethod
    @cache.memoize(timeout=CACHE_TIMEOUT)
    def get_rating_and_color(cls, handle):
        resp = requests.get(cls.API_URL.format(handle=handle))
        if not resp.ok:
            abort(404)
        data = resp.json()

        def _get_color(_rating):
            if _rating < 400:
                return '#808080'
            elif _rating < 800:
                return '#804000'
            elif _rating < 1200:
                return '#008000'
            elif _rating < 1600:
                return '#00C0C0'
            elif _rating < 2000:
                return '#0000FF'
            elif _rating < 2400:
                return '#C0C000'
            elif _rating < 2800:
                return '#FF8000'
            else:
                return '#FF0000'

        if data:
            rating = data[-1]['NewRating']
            color = _get_color(rating)
        else:
            resp = requests.get('{}/{}'.format(cls.PROFILE_URL, handle))
            if not resp.ok:
                abort(404)
            rating = 'unrated'
            color = 'black'
        return rating, color


@app.route('/codeforces/<handle>.svg')
def codeforces_badge(handle):
    return Codeforces.make_response(handle)


@app.route('/topcoder/<handle>.svg')
def topcoder_badge(handle):
    return TopCoder.make_response(handle)


@app.route('/atcoder/<handle>.svg')
def atcoder_badge(handle):
    return AtCoder.make_response(handle)


@app.route('/')
def index():
    return redirect('https://github.com/joonhyungshin/cp-badges')
