-- mart for review analysis, combining reviews with products and customers to analyze review trends and customer feedback
{{ config(
    materialized='incremental',
    unique_key='review_id'
) }}

with reviews as (

    select
        review_id,
        customer_id,
        product_id,
        review_date,
        rating,
        review_text
    from {{ ref('stg_reviews') }}
    {{ incremental_date_filter('review_date') }}
),

products as (

    select
        product_id,
        product_name,
        category_id,
        brand,
        is_active
    from {{ ref('stg_products') }}

),

customers as (

    select
        customer_id,
        first_name,
        last_name,
        city,
        country,
        customer_status
    from {{ ref('stg_customers') }}

),

final as (

    select
        r.review_id,
        r.customer_id,
        c.first_name,
        c.last_name,
        c.city as customer_city,
        c.country as customer_country,
        c.customer_status,

        r.product_id,
        p.product_name,
        p.category_id,
        p.brand,
        p.is_active,

        r.review_date,
        r.rating,
        r.review_text
    from reviews r
    left join products p
        on r.product_id = p.product_id
    left join customers c
        on r.customer_id = c.customer_id

)

select * from final
