with source as (

    select *
    from {{ ref('raw_payments') }}

),

renamed as (

    select
        cast(payment_id as bigint) as payment_id,
        cast(order_id as bigint) as order_id,
        cast(payment_date as date) as payment_date,
        lower(trim(payment_method)) as payment_method,
        lower(trim(payment_status)) as payment_status,
        cast(payment_amount as decimal(18,2)) as payment_amount

    from source

)

select *
from renamed
