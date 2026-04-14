-- mart for order analysis, combining orders with payments and shipments to analyze order lifecycle and customer behavior
-- incremental_strategy='merge' -- to handle updates to existing records as there is a status field
-- incremental_predicates -- check only recent orders (last 30 days) for updates to optimize incremental runs
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    incremental_predicates=["DBT_INTERNAL_DEST.order_date >= current_date - interval '30 day'"]
) }}

with orders as (

    select
        order_id,
        customer_id,
        order_date,
        order_status,
        shipping_city,
        shipping_country
    from {{ ref('stg_orders') }}

    {% if is_incremental() %}
        where order_date >= current_date - interval '30 day'
    {% endif %}

),

latest_payment as (

    select
        order_id,
        payment_id,
        payment_date,
        payment_method,
        payment_status,
        payment_amount,
        -- order can have several payments (e.g. retries), we want the latest one
        row_number() over (
            partition by order_id
            order by payment_date desc, payment_id desc
        ) as rn
    from {{ ref('stg_payments') }}

),

latest_shipment as (

    select
        order_id,
        shipment_id,
        shipment_date,
        delivery_date,
        shipment_status,
        carrier,
        shipping_cost,
        delivery_days,
        -- order can have several shipments (e.g. partial shipments), we want the latest one
        row_number() over (
            partition by order_id
            order by shipment_date desc, shipment_id desc
        ) as rn
    from {{ ref('stg_shipments') }}

),

final as (

    select
        o.order_id,
        o.customer_id,
        o.order_date,
        o.order_status,
        o.shipping_city,
        o.shipping_country,

        p.payment_id,
        p.payment_date,
        p.payment_method,
        p.payment_status,
        p.payment_amount,

        s.shipment_id,
        s.shipment_date,
        s.delivery_date,
        s.shipment_status,
        s.carrier,
        s.shipping_cost,
        s.delivery_days,

        -- assign a sequential number to each order for a customer to track order history
        row_number() over (
            partition by o.customer_id
            order by o.order_date, o.order_id
        ) as customer_order_number,

        -- take the previous order date for the same customer to analyze repeat purchase behavior
        lag(o.order_date) over (
            partition by o.customer_id
            order by o.order_date, o.order_id
        ) as previous_order_date

    from orders o
    left join latest_payment p
        on o.order_id = p.order_id
       and p.rn = 1 -- only join the latest payment record for each order
    left join latest_shipment s
        on o.order_id = s.order_id
       and s.rn = 1 -- only join the latest shipment record for each order

)

select * from final
