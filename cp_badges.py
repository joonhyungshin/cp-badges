from collections.abc import AsyncIterator
import os
from contextlib import asynccontextmanager
from enum import Enum

import aiohttp
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pybadges import badge
from redis import asyncio as aioredis


session = None

CACHE_TIMEOUT = os.getenv('CACHE_TIMEOUT', 300)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    global session
    session = aiohttp.ClientSession()
    yield

app = FastAPI(lifespan=lifespan)



class Platform:
    @classmethod
    def get_profile_url(cls, handle):
        return cls.PROFILE_URL.format(handle=handle)

    @classmethod
    async def get_rating_and_color(cls, handle):
        raise NotImplementedError

    @classmethod
    async def make_badge(cls, handle, extra_args):
        rating, color = await cls.get_rating_and_color(handle)
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
            if arg in extra_args:
                badge_args[arg] = extra_args.get(arg)
        try:
            return badge(**badge_args)
        except ValueError:
            raise HTTPException(400)

    @classmethod
    async def make_response(cls, handle, extra_args):
        response = Response(
            await cls.make_badge(handle, extra_args),
            media_type='image/svg+xml',
            headers={'Cache-Control': f'max-age={CACHE_TIMEOUT}'}
        )
        return response


class Codeforces(Platform):
    LABEL = 'Codeforces'
    URL = 'https://codeforces.com/'
    API_URL = 'https://codeforces.com/api/user.info'
    PROFILE_URL = 'https://codeforces.com/profile/{handle}'
    LOGO_URL = 'https://codeforces.org/s/0/android-icon-192x192.png'

    @classmethod
    @cache(expire=CACHE_TIMEOUT)
    async def get_rating_and_color(cls, handle):
        resp = await session.get(cls.API_URL, params={'handles': handle})
        if not resp.ok:
            raise HTTPException(404)
        data = await resp.json()
        if data['status'] != 'OK':
            raise HTTPException(404)
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
    API_URL = 'https://api.topcoder.com/v5/members'
    PROFILE_URL = 'https://www.topcoder.com/members/{handle}'
    LOGO_URL = 'https://www.topcoder.com/i/favicon.ico'

    @classmethod
    @cache(expire=CACHE_TIMEOUT)
    async def get_rating_and_color(cls, handle):
        resp = await session.get('{}/{}'.format(cls.API_URL, handle))
        if not resp.ok:
            raise HTTPException(404)
        data = await resp.json()
        if 'error' in data:
            raise HTTPException(404)
        rating_info = data.get('maxRating')
        if rating_info:
            rating = rating_info['rating']
            color = rating_info['ratingColor']
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
    @cache(expire=CACHE_TIMEOUT)
    async def get_rating_and_color(cls, handle):
        resp = await session.get(cls.API_URL.format(handle=handle))
        if not resp.ok:
            raise HTTPException(404)
        data = await resp.json()

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
            resp = await session.get('{}/{}'.format(cls.PROFILE_URL, handle))
            if not resp.ok:
                raise HTTPException(404)
            rating = 'unrated'
            color = 'black'
        return rating, color


@app.get('/codeforces/{handle}.svg')
async def codeforces_badge(handle, request: Request):
    return await Codeforces.make_response(handle, request.query_params)


@app.get('/topcoder/{handle}.svg')
async def topcoder_badge(handle, request: Request):
    return await TopCoder.make_response(handle, request.query_params)


@app.get('/atcoder/{handle}.svg')
async def atcoder_badge(handle, request: Request):
    return await AtCoder.make_response(handle, request.query_params)


@app.get('/')
async def index():
    return RedirectResponse('https://github.com/joonhyungshin/cp-badges')
