-- Requirements:
-- 1. Read data from {{ ref('stg_earthquakes') }}.
-- 2. Group earthquakes by event date.
-- 3. Calculate the number of earthquakes per day.
-- 4. Calculate average magnitude, rounded to two decimal places.
-- 5. Calculate maximum magnitude.
-- 6. Calculate average depth, rounded to two decimal places.
-- 7. Name the output columns exactly as shown in the example table.

select
    CAST(event_time AS DATE) as event_date,
    count(*) as earthquake_count,
    round(avg(magnitude), 2) as avg_magnitude,
    round(max(magnitude), 2) as max_magnitude,
    round(avg(depth_km), 2) as avg_depth_km
from {{ ref('stg_earthquakes') }}
group by CAST(event_time AS DATE)