with source as (

    select *
    from {{ ref('raw_products') }}

),

renamed as (

    select
        cast(product_id as bigint) as product_id,
        trim(product_name) as product_name,
        cast(category_id as bigint) as category_id,
        trim(brand) as brand,
        cast(price as decimal(18,2)) as price,
        cast(cost as decimal(18,2)) as cost,
        cast(is_active as boolean) as is_active,
        cast(created_at as date) as created_at

    from source

)

select *
from renamed
