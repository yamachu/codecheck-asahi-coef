# -*- coding: utf-8 -*-
import urllib.request, urllib.parse
import json
import asyncio
import aiohttp

class AsahiNewsAPI:
    BASE_URL = 'http://54.92.123.84/search'

    def __init__(self, access_key = None):
        self.access_key = access_key


    async def search_async(self, query='*:*', sort=None, start=1, rows=10, wt='json'):
        params = {
            'q': query,
            # 'sort': sort, -> 今後対応
            'start': start,
            'rows': rows,
            'wt': wt,
            'ackey': self.access_key
        }
        encoded_params = urllib.parse.urlencode(params, safe = ':[]')
        get_url = self.BASE_URL + '?' + encoded_params

        async with aiohttp.get(get_url) as resp:
            body = await resp.text()
            return json.loads(body)


    def search(self, query='*:*', sort=None, start=1, rows=10, wt='json'):
        params = {
            'q': query,
            # 'sort': sort, -> 今後対応
            'start': start,
            'rows': rows,
            'wt': wt,
            'ackey': self.access_key
        }
        encoded_params = urllib.parse.urlencode(params, safe = ':[]')
        get_url = self.BASE_URL + '?' + encoded_params

        with urllib.request.urlopen(get_url) as resp:
            body = resp.read().decode('utf-8')
            return json.loads(body)
        
    