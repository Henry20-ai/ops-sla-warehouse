with tickets as (

    select * from {{ ref('stg_tickets') }}

),

sla_targets as (

    select
        *,
        case priority
            when 'Urgent' then 4
            when 'High' then 24
            when 'Medium' then 72
            when 'Low' then 120
        end as sla_target_hours

    from tickets

),

flagged as (

    select
        ticket_id,
        customer_name,
        category,
        priority,
        status,
        created_at,
        resolved_at,
        resolution_hours,
        sla_target_hours,
        case
            when status not in ('Resolved', 'Closed') then 'Still Open'
            when resolution_hours > sla_target_hours then 'Breached'
            else 'Met SLA'
        end as sla_status

    from sla_targets

)

select * from flagged