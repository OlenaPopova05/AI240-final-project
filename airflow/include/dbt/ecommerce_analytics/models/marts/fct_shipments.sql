-- mart for shipment analysis, combining shipments with orders to analyze delivery performance and shipping trends
{{ config(
    materialized='incremental',
    unique_key='shipment_id'
) }}

with shipments as (

    select
        shipment_id,
        order_id,
        shipment_date,
        delivery_date,
        shipment_status,
        carrier,
        shipping_cost,
        delivery_days
    from {{ ref('stg_shipments') }}
    {{ incremental_date_filter('shipment_date') }}
),

orders as (

    select
        order_id,
        customer_id,
        order_date,
        order_status,
        shipping_city,
        shipping_country
    from {{ ref('stg_orders') }}

),

final as (

    select
        s.shipment_id,
        s.order_id,
        o.customer_id,
        o.order_date,
        o.order_status,
        s.shipment_date,
        s.delivery_date,
        s.shipment_status,
        s.carrier,
        s.shipping_cost,
        s.delivery_days,
        o.shipping_city,
        o.shipping_country
    from shipments s
    left join orders o
        on s.order_id = o.order_id

)

select * from final
