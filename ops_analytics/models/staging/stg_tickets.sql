with source as (

    select * from {{ source('raw', 'raw_tickets') }}

),

renamed as (

    select
        ticket_id,
        customer_name,
        category,
        priority,
        status,
        created_at,
        resolved_at,
        case
            when status not in ('Resolved', 'Closed') then null
            else extract(epoch from (resolved_at - created_at)) / 3600
        end as resolution_hours

    from source

)

select * from renamed