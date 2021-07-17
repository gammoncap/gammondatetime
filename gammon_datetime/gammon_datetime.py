from datetime import datetime, timedelta
import dateutil
import pytz
from dateutil.parser import parse, isoparse

from crypto.gammon_datetime.exceptions import InvalidDTypeForConstructor, InvalidNumberOfDigits
from crypto.gammon_datetime.utils import closest_lower_neighbor, get_funding_hour_list_for_exchange, \
    closest_upper_neighbor, ndigits


class GammonDateTime(object):

    def __init__(self, dt):

        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise InvalidDTypeForConstructor("dt argument must be timezone aware")
        if dt.tzinfo not in [pytz.UTC, dateutil.tz.tz.tzutc] and dt.tzinfo.utcoffset(dt) !=timedelta(0):
            raise InvalidDTypeForConstructor("dt argument must have UTC as timezone")
        if not isinstance(dt, datetime):
            raise InvalidDTypeForConstructor("dt argument must be a datetime.datetime")

        self.dt = dt
        self.internal_representation = dt.timestamp()

    def __float__(self):
        return self.as_float_sec()


    @classmethod
    def from_string(cls, s):
        dt = parse(s)
        return GammonDateTime(dt)

    @classmethod
    def from_ISO8601_Z_format(cls, s):
        if type(s) == GammonDateTime:
            return s
        if 'Z' not in s or 'T' not in s:
            raise InvalidDTypeForConstructor(
                'Input string must include T and end with Z')
        dt = isoparse(s)
        return GammonDateTime(dt)

    @classmethod
    def from_int_ns(cls, i):
        if type(i) == GammonDateTime:
            return i
        i = int(i) if type(i)==str else i
        dt = datetime.fromtimestamp(i // (1000 * 1000 * 1000), tz=pytz.utc)
        return GammonDateTime(dt)

    @classmethod
    def from_int_μs(cls, i):
        dt = datetime.fromtimestamp(i // (1000 * 1000), tz=pytz.utc)
        return GammonDateTime(dt)

    @classmethod
    def from_int_ms(cls, i):
        if isinstance(i, str):
            i = int(i)
        dt = datetime.fromtimestamp(i // 1000, tz=pytz.utc)
        return GammonDateTime(dt)

    @classmethod
    def from_int_sec(cls, i):
        dt = datetime.fromtimestamp(i, tz=pytz.utc)
        return GammonDateTime(dt)

    @classmethod
    def from_huobi_int_ms(cls, i):
        dt = datetime.fromtimestamp(i//1000 - 8*3600, tz=pytz.utc)
        return GammonDateTime(dt)

    @classmethod
    def utc_now(cls):
        return GammonDateTime(datetime.now(tz=pytz.utc))


    def as_float_sec(self):
        return self.internal_representation

    def to_int_sec(self):
        return int(round(self.internal_representation))

    def to_int_ms(self):
        return int(round(self.internal_representation * 1000))

    def to_int_μs(self):
        return int(round(self.internal_representation * 1000 * 1000))

    def to_int_ns(self):
        return int(round(self.internal_representation * 1000 * 1000 * 1000))

    def to_ISO8601_Z_format(self, INCLUDE_SECOND_FRACTION = True):
        return self.dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if INCLUDE_SECOND_FRACTION else \
            self.dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def to_iso_no_T_no_Z_no_plus(self):
        return self.dt.strftime('%Y-%m-%d %H:%M:%S')

    def to_okex_format(self):
        return self.dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def to_filename(self):
        return self.dt.strftime('%Y-%m-%d-%H%M.csv')

    def format_for_web_app_table(self):
        return self.dt.strftime('%Y-%m-%d %H:%M')

    def __repr__(self):
        return str(self.to_int_ns())

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return GammonDateTime(self.dt - other)
        elif isinstance(other, GammonDateTime):
            return self.dt - other.dt
        elif isinstance(other, datetime):
            return self.dt - other
        elif isinstance(other, int):
            n = ndigits(other)
            if n not in [10,13,16,19]:
                raise InvalidNumberOfDigits(
                    f"""Expected ndigits in [10,13,16,19]
Found {n} digits."""

                )
            return {
                19 : self.subtract_nanosecs,
                16 : self.subtract_microsecs,
                13 : self.subtract_millisecs,
                10 : self.subtract_seconds
            }[n](other)

    def __add__(self, other):
        if isinstance(other, timedelta):
            return GammonDateTime(self.dt + other)
        elif isinstance(other, int):
            n = ndigits(other)
            if n not in [10, 13, 16, 19]:
                raise InvalidNumberOfDigits(
                    f"""Expected ndigits in [10,13,16,19]
    Found {n} digits."""

                )
            return {
                19: self.add_nanosecs,
                16: self.add_microsecs,
                13: self.add_millisecs,
                10: self.add_seconds
            }[n](other)

    def subtract_nanosecs(self, nanos):
        return GammonDateTime.from_int_ns(self.to_int_ns() - nanos)

    def subtract_microsecs(self, micros):
        return GammonDateTime.from_int_μs(self.to_int_μs() - micros)

    def subtract_millisecs(self, millis):
        return GammonDateTime.from_int_ms(self.to_int_ms() - millis)

    def subtract_seconds(self, secs):
        return GammonDateTime.from_int_sec(self.to_int_sec() - secs)


    def add_nanosecs(self, nanos):
        return GammonDateTime.from_int_ns(self.to_int_ns() + nanos)

    def add_microsecs(self, micros):
        return GammonDateTime.from_int_μs(self.to_int_μs() + micros)

    def add_millisecs(self, millis):
        return GammonDateTime.from_int_ms(self.to_int_ms() + millis)

    def add_seconds(self, secs):
        return GammonDateTime.from_int_sec(self.to_int_sec() + secs)

    def __hash__(self):
        return self.to_int_ns()

    def __gt__(self, other):
        if isinstance(other, GammonDateTime):
            return self.dt > other.dt
        elif isinstance(other, datetime):
            return self.dt > other
        else:
            raise InvalidDTypeForConstructor('can only compare with datetime.datetime or GDT objects')


    def __lt__(self, other):
        if isinstance(other, GammonDateTime):
            return self.dt < other.dt
        elif isinstance(other, datetime):
            return self.dt < other
        else:
            raise InvalidDTypeForConstructor('can only compare with datetime.datetime or GDT objects')

    def __le__(self, other):
        return self < other or self == other

    def __eq__(self, other):
        return self.internal_representation == other.internal_representation


    def get_surrounding_funding_times(self, exchange_name):

        now = self.dt.hour + self.dt.minute / 60
        hours = get_funding_hour_list_for_exchange(exchange_name.lower())
        next = closest_upper_neighbor(hours, now)
        prev = closest_lower_neighbor(hours, now)
        if prev < 0:
            yesterday = self.dt - timedelta(days=1)
            prev_dt = GammonDateTime(
                datetime(
                    yesterday.year,
                    yesterday.month,
                    yesterday.day,
                    hour=prev+24,
                    minute=0,
                    second=0,
                    tzinfo=pytz.utc)
                )
        else:
            prev_dt = GammonDateTime(
                datetime(
                    self.dt.year,
                    self.dt.month,
                    self.dt.day,
                    hour=prev,
                    minute=0,
                    second=0,
                    tzinfo=pytz.utc)
            )


        if next >= 24:
            tomorrow = self.dt + timedelta(days=1)
            next_dt = GammonDateTime(
                datetime(
                    tomorrow.year,
                    tomorrow.month,
                    tomorrow.day,
                    hour = next - 24,
                    minute=0,
                    second=0,
                    tzinfo=pytz.utc)
            )
        else:
            today = self.dt.date()
            next_dt = GammonDateTime(
                datetime(
                    today.year,
                    today.month,
                    today.day,
                    hour=next,
                    minute=0,
                    second=0,
                    tzinfo=pytz.utc)
            )

        return prev_dt, next_dt





if __name__ == '__main__':
    import time
    now = GammonDateTime.utc_now()
    ns = now.to_int_ns()
    μ = now.to_int_μs()
    m = now.to_int_ms()
    s = now.to_int_sec()

    for i in [ns, μ, m, s]:
        time.sleep(1)
        print(GammonDateTime.utc_now() - i)

    print(now.to_okex_format())
