#!/usr/bin/env python -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from time import time_ns

import pytz

from gammon_datetime.exceptions import InvalidDTypeForConstructor
from gammon_datetime.gdatetime import GammonDateTime
from gammon_datetime.utils import closest_lower_neighbor, closest_upper_neighbor


class DateTimeTest(unittest.TestCase):

    def test_wrong_datetime(self):
        with self.assertRaises(InvalidDTypeForConstructor):
            dt = datetime.now(pytz.timezone('EST'))
            gdt = GammonDateTime(dt)

    def test_no_datetime_failure(self):
        with self.assertRaises(InvalidDTypeForConstructor):
            gdt = GammonDateTime(datetime.now())

    def test_constructor_with_UTC(self):
        gdt = GammonDateTime(datetime.now(pytz.UTC))
        self.assertTrue(type(gdt.internal_representation)==float)

    def test_from_string_failure_case(self):
        with self.assertRaises(InvalidDTypeForConstructor):
            """
            String is not tz-aware.  Must raise exception.
            """
            s = "2021-04-30T14:48:43.979569000"
            gdt = GammonDateTime.from_string(s)

    def test_from_string_success_case(self):
        s = '2021-05-05 10:11:38.936851+00:00'
        gdt = GammonDateTime.from_string(s)
        self.assertTrue(type(gdt)==GammonDateTime)

class HashibilityTests(unittest.TestCase):

    def test(self):
        gdt = GammonDateTime(datetime.now(pytz.UTC))
        gdt2 = gdt.add_seconds(3600)
        gdt3 = gdt.add_millisecs(3600)
        gdt4 = gdt.add_nanosecs(3600)

        gdtlist = [gdt, gdt2, gdt3, gdt4]
        print(sorted(gdtlist))

class DateTimeFromIntTests(unittest.TestCase):

    def test_from_nanoseconds(self):
        ns = time_ns()
        gdt = GammonDateTime.from_int_ns(ns)

    def test_from_μs(self):
        μs = time_ns()/1000
        gdt = GammonDateTime.from_int_μs(μs)
        self.assertEqual(len(str(gdt)), 19)

    def test_from_millisec(self):
        ms = time_ns()/1000000
        gdt = GammonDateTime.from_int_μs(ms)

    def test_to_int_sec(self):
        s = '2021-05-05 10:11:38.936851+00:00'
        gdt = GammonDateTime.from_string(s)
        i=gdt.to_int_sec()
        self.assertEqual(len(str(i)), 10)

    def test_to_int_ms(self):
        s = '2021-05-05 10:11:38.936851+00:00'
        gdt = GammonDateTime.from_string(s)
        i=gdt.to_int_ms()
        self.assertEqual(len(str(i)), 13)

    def test_to_int_μs(self):
        s = '2021-05-05 10:11:38.936851+00:00'
        gdt = GammonDateTime.from_string(s)
        i = gdt.to_int_μs()
        self.assertEqual(len(str(i)), 16)

    def test_to_int_ns(self):
        s = '2021-05-05 10:11:38.936851+00:00'
        gdt = GammonDateTime.from_string(s)
        i=gdt.to_int_ns()
        self.assertEqual(len(str(i)), 19)

    def test_to_float_sec(self):
        s = '2021-05-05 10:11:38.936851+00:00'
        gdt = GammonDateTime.from_string(s)
        f = gdt.as_float_sec()
        self.assertEqual(type(f), float)

    def test_from_ISO_Z_format(self):
        s = '2021-09-24T08:00:00Z'
        gdt = GammonDateTime.from_ISO8601_Z_format(s)
        self.assertTrue(type(gdt)==GammonDateTime)
        s2 = gdt.to_ISO8601_Z_format(INCLUDE_SECOND_FRACTION=False)
        self.assertEqual(s, s2)

    def test_from_ISO_Z_format2(self):
        s = '2021-09-24T08:00:00' # Z is missing
        with self.assertRaises(InvalidDTypeForConstructor):
            gdt = GammonDateTime.from_ISO8601_Z_format(s)

class TakeClosestTest(unittest.TestCase):

    def test_below(self):
        mylist = [1,3,5,7,9,11,13,15]
        mynumber = 8.5
        result = closest_lower_neighbor(mylist, mynumber)
        self.assertEqual(result, 7)

    def test_above(self):
        mylist = [1,3,5,7,9,11,13,15]
        mynumber = 9.5
        result = closest_upper_neighbor(mylist, mynumber)
        self.assertEqual(result, 11)




class NeighboringFundingTimesTest(unittest.TestCase):

    def test_kucoin(self):
        s = '2021-09-24T08:15:00Z'
        gdt = GammonDateTime.from_ISO8601_Z_format(s)
        before, after = gdt.get_surrounding_funding_times('kucoin')
        self.assertLess(before, after)
        self.assertEqual((after - before).seconds, 8 * 3600)

    def test_kucoin2(self):
        s = '2021-09-24T00:15:00Z'
        gdt = GammonDateTime.from_ISO8601_Z_format(s)
        before, after = gdt.get_surrounding_funding_times('kucoin')
        self.assertLess(before, after)
        self.assertEqual((after - before).seconds, 8 * 3600)


    def test_bybit(self):
        s = '2021-09-24T23:59:00Z'
        gdt = GammonDateTime.from_ISO8601_Z_format(s)
        before, after = gdt.get_surrounding_funding_times('bybit')
        self.assertLess(before, after)
        self.assertEqual((after - before).seconds, 8 * 3600)


    def test_dydx(self):
        s = '2021-09-24T08:15:00Z'
        gdt = GammonDateTime.from_ISO8601_Z_format(s)
        before, after = gdt.get_surrounding_funding_times('DYDX')
        self.assertTrue(before.dt.minute==0)
        self.assertTrue(after.dt.minute==0)
        self.assertLess(before, after)
        self.assertEqual((after - before).seconds, 3600)

    def test_dydx2(self):
        gdt = GammonDateTime.utc_now()
        before, after = gdt.get_surrounding_funding_times('dydx')
        self.assertTrue(before.dt.minute==0)
        self.assertTrue(after.dt.minute==0)
        self.assertLess(before, after)
        self.assertEqual((after - before).seconds, 3600)




if __name__ == '__main__':
    unittest.main()