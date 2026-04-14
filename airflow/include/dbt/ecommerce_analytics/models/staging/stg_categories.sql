with source as (

    select *
    from {{ ref('raw_categories') }}

),

renamed as (

    select
        cast(category_id as bigint) as category_id,
        trim(category_name) as category_name,
        trim(department_name) as department_name

    from source

)

select *
from renamed
