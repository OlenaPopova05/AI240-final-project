with source as (

    select *
    from {{ ref('raw_reviews') }}

),

renamed as (

    select
        cast(review_id as bigint) as review_id,
        cast(customer_id as bigint) as customer_id,
        cast(product_id as bigint) as product_id,
        cast(review_date as date) as review_date,
        cast(rating as bigint) as rating,
        trim(review_text) as review_text

    from source

)

select *
from renamed
