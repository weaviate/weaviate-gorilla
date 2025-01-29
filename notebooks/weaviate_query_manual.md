# Course Management System Query Guide

## Course Queries

### Finding Open Courses
To search for currently available courses:
```sql
"Which courses are currently open for enrollment?"
```
Verify that 'currentlyEnrolling' is set to 'True'.

### Duration Filters
Filter courses by duration thresholds:
- Under 10 hours
- Under 20 hours
- Under 40 hours

### Topic-Based Search
- Include relevant keywords in course descriptions
- Check course titles for key outcomes if initial search yields no results
- Use specific terms like "capstone project" in search queries

## Instructor Queries

### Experience and Qualifications
For experienced faculty:
```sql
"Which instructors have over 10 years of teaching experience?"
```
Reference the 'yearsOfTeaching' field.

To view biographical information:
```sql
"Show me the biography of the instructor named [Instructor's Name]"
```
Note: Exact spelling is required.

### Tenure Status
To identify tenured faculty:
```sql
"Which instructors are tenured?"
```
Verify 'tenured' is set to 'True'.

### Career Length
To find the most experienced instructor:
```sql
"Who has the longest teaching career among all instructors?"
```
Check 'yearsOfTeaching' for maximum value.

### Teaching Philosophy
For specific teaching approaches:
```sql
"Which instructors mention a 'hands-on learning' philosophy in their biography?"
```
Search the 'biography' field for relevant terms.

### Combined Queries
For complex instructor searches:
```sql
"Which instructors have a biography mentioning '[specific teaching method]' and have been teaching for more than [number] years?"
```
Check both 'biography' and 'yearsOfTeaching' fields.

For tenured instructors with specific methods:
```sql
"Which tenured instructors have a teaching philosophy related to '[specific teaching method]'?"
```
Ensure:
- 'tenured' is 'True'
- Search 'biography' field for teaching method

## Student Information

### Enrollment Status
To view full-time students:
```sql
"List all students who are enrolled full-time"
```
Verify 'enrolledFullTime' is 'True'.

### Credit Status
For credit-based searches:
```sql
"Which students have completed more than 30 credits?"
```
Check 'completedCredits' field.

For part-time students with significant credits:
```sql
"Show me all students who have completed at least 20 credits but are not enrolled full-time"
```
Ensure:
- 'completedCredits' ≥ 20
- 'enrolledFullTime' is 'False'

### Research Interests
To view individual research interests:
```sql
"Show me the research interests of the student named [Student's Name]"
```
Note: Exact spelling is required.

For topic-specific searches:
```sql
"Find students with research interests in [specific topic]"
```
Search the 'researchInterests' field for relevant keywords.