#!/usr/bin/env python3

import json
import collections
import datetime
import asyncio
import aiohttp
from .AsahiNewsArchives.api import AsahiNewsAPI
import numpy
# for debug
# from pprint import pprint

def _strdate_to_datetime(strdate):
    return datetime.date(*[int(part_ymd) for part_ymd in strdate.split('-')])


def _parse_keywords(base_keyword):
    return [''.join(words.strip()[1:-1]).encode('utf-8', 'surrogateescape').decode('utf-8', 'surrogateescape')
        for words in base_keyword[1:-1].split(',')]


def _generate_floor_day_week_list(str_start_day, str_end_day):
    start_day = _strdate_to_datetime(str_start_day)
    end_day = _strdate_to_datetime(str_end_day)
    total_week = ((end_day - start_day).days + 1) // 7

    week_list = []

    for i in range(total_week):
        _start = start_day + datetime.timedelta(days=7*i)
        _end = _start + datetime.timedelta(days=6)

        week_list.append({
            "start": _start,
            "end": _end
        })

    return week_list


async def _search_per_week(keyword, week_list):
    api = AsahiNewsAPI("869388c0968ae503614699f99e09d960f9ad3e12")
    async def _inner_search_per_week(keyword, week):
        response = await api.search_async(
            query='Body:{} AND ReleaseDate:[{} TO {}]'
                .format(keyword,
                        week['start'].strftime('%Y-%m-%d'),
                        week['end'].strftime('%Y-%m-%d')),
            rows=1
        )
        
        return int(response['response']['result']['numFound'])

    tasks = [_inner_search_per_week(keyword, week) for week in week_list]
    result = await asyncio.gather(*tasks)

    return result


def _calc_coef_to_get_tri_mat(responses):
    non_same_pos = 0
    items = list(responses.items())

    keyword_sums = numpy.zeros(len(responses), numpy.int)
    coef_mat = numpy.empty(
        (1 + len(responses)) * len(responses) // 2,
        numpy.double
    )

    for i, item in enumerate(responses):
        keyword_sums[i] = sum(responses[item])

    for i in range(len(responses)):
        for j in range(i):
            if keyword_sums[i] != 0 and keyword_sums[j] != 0:
                coef_mat[non_same_pos] = numpy.corrcoef(
                    items[i][1], items[j][1]
                )[0, 1]
            else:
                coef_mat[non_same_pos] = numpy.NaN
            non_same_pos += 1

    return coef_mat


def main(argv):
    from pprint import pprint
    result = collections.OrderedDict()
    keywords = _parse_keywords(argv[0])
    week_list = _generate_floor_day_week_list(*argv[1:3])

    loop = asyncio.get_event_loop()
    for keyword in keywords:
        result.update({keyword: loop.run_until_complete(_search_per_week(keyword, week_list))})

    coef_mat = _calc_coef_to_get_tri_mat(result)

    tmp_len = len(result)
    coef_arr = [[None for _ in range(tmp_len)] for _ in range(tmp_len)]

    idx = 0
    for i in range(tmp_len):
        coef_arr[i][i] = '1'
        for j in range(i):
            if not numpy.isnan(coef_mat[idx]):
                coef_arr[i][j] = str(round(coef_mat[idx],3))
                coef_arr[j][i] = coef_arr[i][j]
            else:
                coef_arr[i][j] = 'null'
                coef_arr[j][i] = coef_arr[i][j]
            idx += 1

    output = '{"coefficients":['
    for outter in coef_arr:
        output += '['
        for val in outter:
            output += val
            output += ','
        output = output[:-1]
        output += '],'
    output = output[:-1]
    output += ']'

    output += ',"posChecker":'

    # do check
    output += 'true'
    
    output += '}'

    print(output)



