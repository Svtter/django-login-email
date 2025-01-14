import datetime


def transform_timestamp(ts: int) -> datetime.datetime:
  return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
