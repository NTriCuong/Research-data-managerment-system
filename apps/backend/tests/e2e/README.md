# End-to-End Tests

`test_research_publication_workflow.py` covers the complete SRS publication flow:

`create staging -> upload file -> submit -> reviewer forward -> approver approve -> core record -> search -> logs`

It then creates a revision from the approved core record, approves it again, and verifies that
the same core record is updated to version 2 with a metadata-version snapshot.

PostgreSQL is real; only the external R2 upload call is mocked.
