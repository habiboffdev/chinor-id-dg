-- ========================================
-- 🔴 CRITICAL: Database Audit Queries
-- Find Invalid Applications
-- ========================================

-- Query 1: Applications with missing required question answers
-- ========================================
-- This finds applications where required questions were not answered
SELECT 
    a.id as application_id,
    a.applied_at,
    s.user_id,
    CONCAT(u.first_name, ' ', u.last_name) as student_name,
    u.email as student_email,
    o.id as opportunity_id,
    o.title as opportunity_title,
    org.name as organization_name,
    COUNT(DISTINCT rq.id) as required_questions_total,
    COUNT(DISTINCT aa.id) as provided_answers,
    (COUNT(DISTINCT rq.id) - COUNT(DISTINCT aa.id)) as missing_answers_count
FROM applications_application a
JOIN students_studentprofile s ON a.student_id = s.id
JOIN accounts_user u ON s.user_id = u.id
JOIN opportunities_opportunity o ON a.opportunity_id = o.id
JOIN organizations_organization org ON o.organization_id = org.id
LEFT JOIN opportunities_opportunityquestion rq 
    ON rq.opportunity_id = o.id AND rq.is_required = true
LEFT JOIN applications_applicationanswer aa 
    ON aa.application_id = a.id AND aa.question_id = rq.id
GROUP BY a.id, a.applied_at, s.user_id, u.first_name, u.last_name, 
         u.email, o.id, o.title, org.name
HAVING COUNT(DISTINCT rq.id) > 0 
   AND COUNT(DISTINCT rq.id) > COUNT(DISTINCT aa.id)
ORDER BY a.applied_at DESC;

-- Expected result: 0 rows after fix deployed
-- Any rows found indicate applications that bypassed validation


-- Query 2: Applications with empty/whitespace-only answers
-- ========================================
-- This finds answers to required questions that are empty or whitespace
SELECT 
    a.id as application_id,
    a.applied_at,
    CONCAT(u.first_name, ' ', u.last_name) as student_name,
    u.email as student_email,
    o.title as opportunity_title,
    oq.id as question_id,
    oq.question,
    oq.is_required,
    aa.answer_text,
    LENGTH(aa.answer_text) as answer_length,
    LENGTH(TRIM(aa.answer_text)) as trimmed_length
FROM applications_applicationanswer aa
JOIN applications_application a ON aa.application_id = a.id
JOIN students_studentprofile s ON a.student_id = s.id
JOIN accounts_user u ON s.user_id = u.id
JOIN opportunities_opportunity o ON a.opportunity_id = o.id
JOIN opportunities_opportunityquestion oq ON aa.question_id = oq.id
WHERE oq.is_required = true
  AND (aa.answer_text IS NULL 
       OR TRIM(aa.answer_text) = ''
       OR LENGTH(TRIM(aa.answer_text)) = 0)
ORDER BY a.applied_at DESC;

-- Expected result: 0 rows
-- Any rows found indicate empty required answers that bypassed validation


-- Query 3: Summary statistics by opportunity
-- ========================================
-- Shows which opportunities have the most validation issues
SELECT 
    o.id as opportunity_id,
    o.title,
    org.name as organization_name,
    o.status,
    COUNT(DISTINCT a.id) as total_applications,
    COUNT(DISTINCT rq.id) as required_questions_count,
    COUNT(DISTINCT CASE 
        WHEN aa.id IS NULL OR TRIM(aa.answer_text) = '' 
        THEN a.id 
    END) as applications_with_issues
FROM opportunities_opportunity o
JOIN organizations_organization org ON o.organization_id = org.id
LEFT JOIN applications_application a ON a.opportunity_id = o.id
LEFT JOIN opportunities_opportunityquestion rq 
    ON rq.opportunity_id = o.id AND rq.is_required = true
LEFT JOIN applications_applicationanswer aa 
    ON aa.application_id = a.id AND aa.question_id = rq.id
WHERE o.status IN ('published', 'closed')
GROUP BY o.id, o.title, org.name, o.status
HAVING COUNT(DISTINCT rq.id) > 0
ORDER BY applications_with_issues DESC, total_applications DESC;


-- Query 4: Applications created in the last 7 days (recent activity)
-- ========================================
-- Check recent applications for validation compliance
SELECT 
    a.id,
    a.applied_at,
    CONCAT(u.first_name, ' ', u.last_name) as student_name,
    o.title as opportunity_title,
    COUNT(DISTINCT rq.id) as required_questions,
    COUNT(DISTINCT aa.id) as provided_answers,
    CASE 
        WHEN COUNT(DISTINCT rq.id) = COUNT(DISTINCT aa.id) THEN '✅ Valid'
        ELSE '❌ Invalid'
    END as validation_status
FROM applications_application a
JOIN students_studentprofile s ON a.student_id = s.id
JOIN accounts_user u ON s.user_id = u.id
JOIN opportunities_opportunity o ON a.opportunity_id = o.id
LEFT JOIN opportunities_opportunityquestion rq 
    ON rq.opportunity_id = o.id AND rq.is_required = true
LEFT JOIN applications_applicationanswer aa 
    ON aa.application_id = a.id AND aa.question_id = rq.id
WHERE a.applied_at >= NOW() - INTERVAL '7 days'
GROUP BY a.id, a.applied_at, u.first_name, u.last_name, o.title
ORDER BY a.applied_at DESC;


-- Query 5: Find specific required questions that are frequently skipped
-- ========================================
-- Identify which questions cause the most issues
SELECT 
    oq.id as question_id,
    oq.question,
    o.title as opportunity_title,
    COUNT(DISTINCT a.id) as total_applications,
    COUNT(DISTINCT aa.id) as answered_count,
    (COUNT(DISTINCT a.id) - COUNT(DISTINCT aa.id)) as unanswered_count,
    ROUND(
        (COUNT(DISTINCT aa.id)::float / NULLIF(COUNT(DISTINCT a.id), 0) * 100), 
        2
    ) as answer_rate_percent
FROM opportunities_opportunityquestion oq
JOIN opportunities_opportunity o ON oq.opportunity_id = o.id
LEFT JOIN applications_application a ON a.opportunity_id = o.id
LEFT JOIN applications_applicationanswer aa 
    ON aa.question_id = oq.id AND aa.application_id = a.id
WHERE oq.is_required = true
GROUP BY oq.id, oq.question, o.title
HAVING COUNT(DISTINCT a.id) > 0
ORDER BY unanswered_count DESC, total_applications DESC;


-- Query 6: Applications without ANY answers at all
-- ========================================
-- Most severe validation bypass - applications with zero answers
SELECT 
    a.id,
    a.applied_at,
    a.status,
    CONCAT(u.first_name, ' ', u.last_name) as student_name,
    u.email,
    o.title as opportunity_title,
    org.name as organization_name,
    COUNT(rq.id) as required_questions_exist,
    COUNT(aa.id) as total_answers_provided
FROM applications_application a
JOIN students_studentprofile s ON a.student_id = s.id
JOIN accounts_user u ON s.user_id = u.id
JOIN opportunities_opportunity o ON a.opportunity_id = o.id
JOIN organizations_organization org ON o.organization_id = org.id
LEFT JOIN opportunities_opportunityquestion rq 
    ON rq.opportunity_id = o.id AND rq.is_required = true
LEFT JOIN applications_applicationanswer aa ON aa.application_id = a.id
GROUP BY a.id, a.applied_at, a.status, u.first_name, u.last_name, 
         u.email, o.title, org.name
HAVING COUNT(rq.id) > 0 AND COUNT(aa.id) = 0
ORDER BY a.applied_at DESC;


-- ========================================
-- CLEANUP QUERIES (USE WITH CAUTION!)
-- ========================================

-- Query 7: Count of applications that would be deleted
-- ========================================
-- Run this BEFORE any cleanup to see impact
SELECT 
    'Applications with missing answers' as issue_type,
    COUNT(*) as count
FROM applications_application a
WHERE EXISTS (
    SELECT 1 
    FROM opportunities_opportunityquestion rq
    WHERE rq.opportunity_id = a.opportunity_id
      AND rq.is_required = true
      AND NOT EXISTS (
          SELECT 1 
          FROM applications_applicationanswer aa
          WHERE aa.application_id = a.id 
            AND aa.question_id = rq.id
            AND LENGTH(TRIM(aa.answer_text)) > 0
      )
)

UNION ALL

SELECT 
    'Applications with empty answers' as issue_type,
    COUNT(DISTINCT a.id)
FROM applications_application a
JOIN applications_applicationanswer aa ON aa.application_id = a.id
JOIN opportunities_opportunityquestion oq ON aa.question_id = oq.id
WHERE oq.is_required = true
  AND (aa.answer_text IS NULL OR TRIM(aa.answer_text) = '');


-- Query 8: Mark invalid applications (recommended instead of deletion)
-- ========================================
-- Instead of deleting, mark them for review
-- UNCOMMENT AND RUN AFTER REVIEW:

-- UPDATE applications_application
-- SET reviewer_notes = CONCAT(
--     COALESCE(reviewer_notes, ''), 
--     '\n[SYSTEM] Invalid application - missing required question answers. ',
--     'Created before validation fix on ', 
--     CURRENT_DATE
-- )
-- WHERE EXISTS (
--     SELECT 1 
--     FROM opportunities_opportunityquestion rq
--     WHERE rq.opportunity_id = applications_application.opportunity_id
--       AND rq.is_required = true
--       AND NOT EXISTS (
--           SELECT 1 
--           FROM applications_applicationanswer aa
--           WHERE aa.application_id = applications_application.id 
--             AND aa.question_id = rq.id
--             AND LENGTH(TRIM(aa.answer_text)) > 0
--       )
-- );


-- ========================================
-- MONITORING QUERIES (Run daily/weekly)
-- ========================================

-- Query 9: Daily validation check
-- ========================================
SELECT 
    DATE(a.applied_at) as application_date,
    COUNT(DISTINCT a.id) as total_applications,
    COUNT(DISTINCT CASE 
        WHEN EXISTS (
            SELECT 1 FROM opportunities_opportunityquestion rq
            WHERE rq.opportunity_id = a.opportunity_id 
              AND rq.is_required = true
              AND NOT EXISTS (
                  SELECT 1 FROM applications_applicationanswer aa
                  WHERE aa.application_id = a.id 
                    AND aa.question_id = rq.id
                    AND LENGTH(TRIM(aa.answer_text)) > 0
              )
        ) THEN a.id 
    END) as invalid_applications,
    ROUND(
        COUNT(DISTINCT CASE 
            WHEN NOT EXISTS (
                SELECT 1 FROM opportunities_opportunityquestion rq
                WHERE rq.opportunity_id = a.opportunity_id 
                  AND rq.is_required = true
                  AND NOT EXISTS (
                      SELECT 1 FROM applications_applicationanswer aa
                      WHERE aa.application_id = a.id 
                        AND aa.question_id = rq.id
                        AND LENGTH(TRIM(aa.answer_text)) > 0
                  )
            ) THEN a.id 
        END)::float / NULLIF(COUNT(DISTINCT a.id), 0) * 100,
        2
    ) as validation_compliance_percent
FROM applications_application a
WHERE a.applied_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(a.applied_at)
ORDER BY application_date DESC;
