-- mart for payment analysis, combining payments with orders to analyze payment trends and customer behavior
{{ config(
    materialized='incremental',
    unique_key='payment_id'
) }}

with payments as (

    select
        payment_id,
        order_id,
        payment_date,
        payment_method,
        payment_status,
        payment_amount
    from {{ ref('stg_payments') }}
    {{ incremental_date_filter('payment_date') }}
),

orders as (

    select
        order_id,
        customer_id,
        order_date,
        order_status
    from {{ ref('stg_orders') }}

),

final as (

    select
        p.payment_id,
        p.order_id,
        o.customer_id,
        o.order_date,
        o.order_status,
        p.payment_date,
        p.payment_method,
        p.payment_status,
        p.payment_amount
    from payments p
    left join orders o
        on p.order_id = o.order_id

)

select * from final
