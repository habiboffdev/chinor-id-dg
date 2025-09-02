# Opportunity fields (backend reference)

Source: `opportuni_backend/apps/opportunities/models.py` and serializers.

Core
- title: string (max 200)
- description: text (rich text allowed client-side)
- opportunity_type: enum [internship, volunteer, competition, scholarship, job, workshop, conference]
- status: enum [draft, published, closed, cancelled] (default draft)

Dates
- application_deadline: datetime (ISO, e.g., 2025-08-27T18:00:00Z)
- start_date: date (YYYY-MM-DD)
- end_date: date (optional)

Eligibility
- required_skills: ManyToMany Skill (IDs when writing)
- min_gpa: decimal(3,2) optional
- required_major: string optional
- graduation_year_min / graduation_year_max: integer optional

Details
- location: string
- is_remote: boolean
- compensation: string optional
- benefits: text optional
- cover_image: image optional (upload endpoint separate)

Meta
- max_applications: integer optional
- featured: boolean

Collections
- requirements: list of { requirement, is_mandatory (bool), order (int) }
- additional_questions: list of {
  question, question_type (text, textarea, number, email, url, date, file, select, checkbox),
  is_required (bool), placeholder, help_text, order (int), options (array for select/checkbox),
  max_length (int optional), min_length (int optional)
}

Notes
- Create/Update accepts `requirements`, `additional_questions`, and `required_skills` (IDs).
- For `application_deadline`, send full ISO datetime. The UI uses `datetime-local` and converts to ISO.
- Consider `publish` action via dedicated endpoint if needed after saving a draft.
