import os

from flask import Flask, abort, redirect

import requests


app = Flask(__name__)

SHIELD_IO_BADGE_URL = os.getenv('SHIELD_IO_BADGE_URL', 'https://img.shields.io/badge')

CODEFORCES_API_URL = os.getenv('CODEFORCES_API_URL', 'https://codeforces.com/api/user.info')
CODEFORCES_LOGO_B64 = os.getenv('CODEFORCES_LOGO_B64')


@app.route('/codeforces/<handle>')
def codeforces_badge(handle):
    resp = requests.get(CODEFORCES_API_URL, params={'handles': handle})
    if not resp.ok:
        abort(404)
    data = resp.json()
    if data['status'] != 'OK':
        abort(404)
    user = data['result'][0]
    rank = user['rank']
    rating = user['rating']
    color_dict = {
        'legendary grandmaster': 'red',
        'international grandmaster': 'red',
        'grandmaster': 'red',
        'international master': 'orange',
        'master': 'orange',
        'candidate master': 'purple',
        'expert': 'blue',
        'specialist': 'cyan',
        'pupil': 'green',
        'newbie': 'gray',
    }
    color = color_dict.get(rank, 'black')
    rating = rating or 'unrated'
    badge_url = '{}/Codeforces-{}-{}?logo={}'.format(SHIELD_IO_BADGE_URL, rating, color, CODEFORCES_LOGO_B64)
    return redirect(badge_url)
