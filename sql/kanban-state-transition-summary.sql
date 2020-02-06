-- summarise when stories move between columns of the kanban board
--
-- parameters:
--     temporal scope (date/time range)
--     which project?
--
-- should this query hard-code names for state transitions ???
--     e.g. foo -> bar as "do the thing"
--

select
    CASE
        WHEN (transition ->> 0 != 'New' OR transition ->> 0 != 'Some future sprint')
        AND transition ->> 1 = 'In progress'
        THEN 'Started'
		
        WHEN (transition ->> 0 = 'In progress' OR transition ->> 0 = 'Backlog' OR transition ->> 0 = 'New')
        AND (transition ->> 1 = 'Some future sprint' OR transition ->> 1 = 'New')
        THEN 'Decreased scope'
	
        WHEN (transition ->> 0 = 'Some future sprint' OR transition ->> 0 = 'New')
        AND (transition ->> 1 = 'In progress' OR transition ->> 1 = 'Backlog')
        THEN 'Increased scope'

        WHEN transition ->> 0 != 'Failed QA'
        AND transition ->> 1 = 'Ready for review'
        THEN 'Developed'

        WHEN transition ->> 1 = 'Failed QA'
        THEN 'Rejected'

        WHEN transition ->> 0 = 'Failed QA'
        AND transition ->> 1 = 'Ready for review' 
        THEN 'Fixed'

        WHEN transition ->> 0 != 'Backlog'
        AND transition ->> 1 = 'Done'
        THEN 'Delivered'

        WHEN transition ->> 0 = 'Backlog'
        AND transition ->> 1 = 'Done'
        THEN 'OTBE'
	
        ELSE 'Other'
    END as transition_action,
    count(*)
from
    (
        select
            data#>'{values_diff, status}' as "transition",  -- CASE statement to swap these for labels
            data#>'{userstory, id}' as "user_story_id",
            data#>'{userstory, ref}' as "user_story_ref", -- what is this? TODO figure that out
            data#>'{userstory, subject}' as "user_story_subject", -- make join on userstory.ud to get current subject?
            created,
	    content_type_id
        from
            timeline_timeline
        where
            -- we care about changes to user stories
            event_type='userstories.userstory.change'
            -- ignore comments etc, we only want state (column) changes
            and data#>'{values_diff, status}' ->>0 is not null
            and data#>'{values_diff, status}' ->>1 is not null
            ---------------------------------------------
            -- TODO: parameterise by project namespace --
            ---------------------------------------------
            AND namespace = 'project:11' -- this is the project identifier and place to de-dupe timeline events from users
    ) q
WHERE
    -------------------------------------
    -- TODO: parameterise by timeframe --
    -------------------------------------
    created < to_timestamp('20191211', 'YYYYMMDD')
    AND created > to_timestamp('20191211', 'YYYYMMDD') - interval '1 day'
group by
    transition_action
order by
    count(*) desc;
