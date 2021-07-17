import math
from datetime import datetime

import numpy
import pytz

EPOCH = datetime(1970, 1, 1, tzinfo=pytz.utc)

def closest_upper_neighbor(myList, myNumber):
    myArr = numpy.array(myList)
    return myArr[myArr > myNumber].min()

def closest_lower_neighbor(myList, myNumber):
    myArr = numpy.array(myList)
    return myArr[myArr < myNumber].max()


funding_time_data = {
    'ftx': {
        'window': 1,
        'reference' : 0},
    'dydx': {
        'window': 1,
        'reference': 0},
    'binance': {
        'window': 8,
        'reference': 0},
    'bybit': {
        'window': 8,
        'reference': 0},
    'kucoin': {
        'window': 8,
        'reference': 4},
    'bitmex': {
        'window': 8,
        'reference': 4},
    'okex': {
        'window': 8,
        'reference': 0}
}


def get_funding_hour_list_for_exchange(exchange):
    w = funding_time_data[exchange]['window']
    ref = funding_time_data[exchange]['reference']

    if w == 8:
        return [(ref + i * w) for i in range(-3,4)]
    elif w==1:
        return [(i * w) for i in range(-1, 26)]


def ndigits(i):
    return math.ceil(math.log10(i))


if __name__ == '__main__':
    myList = get_funding_hour_list_for_exchange('dydx')
    print(closest_lower_neighbor(myList, 23.2))
    print(closest_upper_neighbor(myList, 23.2))



