select * from {{ source('minio', 'raw_shipments') }}

