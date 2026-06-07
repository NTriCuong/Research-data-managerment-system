# Database Tests

These tests execute against PostgreSQL from `TEST_DATABASE_URL` and verify:

- metadata quality gives no year points when `year IS NULL`
- username/email can be reused after a user is soft-deleted
- workflow history cannot be orphaned
- active core identifiers are unique, while soft-deleted identifiers can be reused
- FTS includes authors and keywords
- Vietnamese FTS works with accented and unaccented queries

The test database must already be migrated. A CI job that creates a blank database and runs
`alembic upgrade head` is still required to verify the complete migration-from-zero process.
