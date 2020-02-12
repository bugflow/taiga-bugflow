-- summarise when stories move between columns of the kanban board
--
-- parameters:
--     temporal scope (date/time range)
--     which project?
--
-- this query hard-codes names for state transitions:
--     e.g. foo -> bar as "do the thing"
--
-- This is a query template.
-- It is designed to have variable substitution like so
--
--    tmpl = open(<path-to-this-file>, r).read()
--    query = tmpl.format(
--        project_id=project_id,
--        since=since,
--        until=until
--    )
--

SELECT
    ms.transition
	, 
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
		
		WHEN transition ->> 0 = 'Failed QA'
		AND transition ->> 1 = 'Backlog'
		THEN 'Did not resolve'
		
		ELSE 'Unknown'
	END as transition_action
	, ms.user_story_ref
	, ms.user_story_subject
	, ms.created
	, rp.point_values
FROM
(
	SELECT
		data#>'{{values_diff, status}}' as "transition", 
		-- The story ID can actually change in the timeline, for some reason
		-- so we may as well look it up while we're here based on the ref
		(
			SELECT id from userstories_userstory
			WHERE text(ref) = data#>>'{{userstory, ref}}'
			-- if MULTIPLES, ignore all but the most recently created
			ORDER BY created_date
			LIMIT 1
		) as "user_story_id",
		data#>'{{userstory, ref}}' as "user_story_ref",
		data#>'{{userstory, subject}}' as "user_story_subject", 
		created,
		content_type_id
	FROM timeline_timeline
	-- we care about changes to user stories
	WHERE event_type='userstories.userstory.change'
	AND (
		data#>'{{values_diff, status}}' ->>0 IS NOT null
		AND data#>'{{values_diff, status}}' ->>1 IS NOT null
	)
	AND namespace = 'project:{project_id}'
) AS ms

LEFT OUTER JOIN (
	SELECT
		user_story_id, 
		SUM(point_values) as point_values 
	FROM (
		SELECT 
			user_story_id
			, (
				SELECT value FROM projects_points
				WHERE id = rolepoints.points_id
			) "point_values"
		FROM userstories_rolepoints AS rolepoints
	) as sub_query
	WHERE sub_query.point_values IS NOT NULL
	GROUP BY sub_query.user_story_id
) AS rp ON (
	text(rp.user_story_id) = text(ms.user_story_id)
)

WHERE
    created < to_timestamp('{until}', 'YYYY-MM-DD-HH24:MI:SS:US')
    AND created > to_timestamp('{since}', 'YYYY-MM-DD-HH24:MI:SS:US')
ORDER BY
    user_story_ref,
    created DESC;
