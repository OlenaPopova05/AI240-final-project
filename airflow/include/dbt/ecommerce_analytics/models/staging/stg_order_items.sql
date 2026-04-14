with source as (

    select *
    from {{ ref('raw_order_items') }}

),

renamed as (

    select
        cast(order_item_id as bigint) as order_item_id,
        cast(order_id as bigint) as order_id,
        cast(product_id as bigint) as product_id,
        cast(quantity as bigint) as quantity,
        cast(unit_price as decimal(18,2)) as unit_price,
        cast(discount_amount as decimal(18,2)) as discount_amount

    from source

),

final as (

    select
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        discount_amount,
        quantity * unit_price as revenue_before_discount,
        (quantity * unit_price) - discount_amount as revenue_after_discount

    from renamed

)

select *
from final
