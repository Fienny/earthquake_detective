select *
from {{ ref('stg_earthquakes') }}
where 1=1
    and (
        latitude < -90 
        or latitude > 90
        or longitude < -180 
        or longitude > 180
        or latitude is null
        or longitude is null
    )
    
