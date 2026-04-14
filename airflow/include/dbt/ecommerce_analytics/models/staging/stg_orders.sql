with source as (

    select *
    from {{ ref('raw_orders') }}

),

renamed as (

    select
        cast(order_id as bigint) as order_id,
        cast(customer_id as bigint) as customer_id,
        cast(order_date as date) as order_date,
        lower(trim(order_status)) as order_status,
        trim(shipping_city) as shipping_city,
        trim(shipping_country) as shipping_country

    from source

)

select *
from renamed
