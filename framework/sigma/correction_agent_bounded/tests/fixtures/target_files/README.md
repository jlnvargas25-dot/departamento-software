# Fixture target files — correction_agent_bounded tests

Synthetic files with Tier B patterns for testing the correction agent.

| File | Pattern | action_hint |
|------|---------|-------------|
| silent_catch.ts | Empty catch block | inject-logger-with-request-id |
| missing_auth.ts | Server Action without auth | inject-auth-check-with-tenant-scope |
| missing_zod.ts | Server Action without zod | generate-zod-schema-for-input |
| console_fallback.ts | Console fallback without flag | wrap-fallback-in-feature-flag |
| missing_rls.sql | Table without RLS policy | generate-rls-policy-stub |
| missing_request_id.ts | Handler without request ID | inject-request-id-through-stack |
