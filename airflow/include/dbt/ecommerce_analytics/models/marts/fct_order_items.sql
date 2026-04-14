-- mart for order item analysis, combining order items with orders and products to analyze sales performance and product trends
{{ config(
    materialized='incremental',
    unique_key='order_item_id',
    incremental_strategy='merge'
) }}

with order_items as (

    select
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        discount_amount,
        revenue_before_discount,
        revenue_after_discount
    from {{ ref('stg_order_items') }}

),

orders as (

    select
        order_id,
        customer_id,
        order_date,
        order_status
    from {{ ref('stg_orders') }}

    -- for incremental runs only check recent orders (last 7 days) for updates to optimize performance, 
    -- as order items are unlikely to change after a week
    {% if is_incremental() %}
    where order_date >= (
        select max(order_date) - interval '7 day'
        from {{ this }}
    )
    {% endif %}

),

products as (

    select
        product_id,
        product_name,
        category_id,
        brand,
        price,
        cost,
        is_active,
        created_at
    from {{ ref('stg_products') }}

),

categories as (

    select
        category_id,
        category_name
    from {{ ref('stg_categories') }}

),

final as (

    select
        oi.order_item_id,
        oi.order_id,
        o.customer_id,
        o.order_date,
        o.order_status,
        oi.product_id,
        p.product_name,
        p.category_id,
        c.category_name,
        p.brand,
        p.is_active,

        oi.quantity,
        oi.unit_price,
        oi.discount_amount,
        oi.revenue_before_discount,
        oi.revenue_after_discount,

        -- calculate cumulative revenue for the product up to the current order item to analyze sales trends over time
        -- for each product sort rows by date and add current revenue to all previous ones to get a running total
        sum(
            case
                when o.order_status not in ('canceled', 'returned')
                then oi.revenue_after_discount
                else 0
            end
        ) over (
            partition by oi.product_id
            order by o.order_date, oi.order_item_id
        ) as cumulative_product_revenue

    from order_items oi
    inner join orders o
        on oi.order_id = o.order_id
    left join products p
        on oi.product_id = p.product_id
    left join categories c
        on p.category_id = c.category_id

)

select * from final
