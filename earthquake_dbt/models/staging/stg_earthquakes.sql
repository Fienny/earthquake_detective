-- Write a SQL query that:
-- 1. Reads ../data/silver/earthquakes.parquet using DuckDB's read_parquet().
-- 2. Explicitly selects all eight columns from our Silver schema.
-- 3. Filters out records where magnitude is null.
-- 4. Filters out records where magnitude is below 2.5.
-- 5. Orders the results by event_time descending.
-- The columns are:

-- event_id, event_time, updated_at, latitude, longitude, depth_km, magnitude, place.

select
    event_id,
    event_time,
    updated_at,
    latitude,
    longitude,
    depth_km,
    magnitude,
    place
from read_parquet('../data/silver/earthquakes.parquet')
where 1=1
    and magnitude is not null
    and magnitude >= 2.5
order by event_time desc