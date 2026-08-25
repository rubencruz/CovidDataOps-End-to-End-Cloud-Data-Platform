# Production Runbook

## 1. First response

1. Open the Cloud Monitoring dashboard `COVID Data Pipeline — Production`.
2. Identify whether the incident is HTTP failures, latency, application errors or data quality.
3. Capture the `request_id`, `event_id` and `source_object` from Cloud Logging when available.
4. Check the latest Cloud Run revision and deployment time before changing infrastructure.

## 2. Event-driven ingestion failure

- A failed `/events/pubsub` request returns HTTP 500 intentionally so the event delivery path can retry.
- Inspect the Cloud Run logs for the captured `request_id` and source object.
- If the source CSV is invalid, fix or quarantine the input rather than repeatedly retrying it.
- If the failure is transient (GCS/BigQuery/API), allow delivery retries and verify the next attempt succeeds.

## 3. Scheduled job failure

- Cloud Scheduler retries each quality/reconciliation request according to its Terraform retry policy.
- Inspect `/jobs/quality-check` or `/jobs/reconciliation` logs.
- Query the raw BigQuery table for the failed condition before rerunning.
- After remediation, trigger the Scheduler job manually and verify HTTP 200.

## 4. High 5xx rate or latency

- Compare the alert with the most recent Cloud Run revision.
- Check BigQuery load errors, GCS availability and dependency/API errors.
- Roll back to the previous known-good container image using the normal deployment workflow if the release introduced the regression.

## 5. Data-quality incident

- Treat a failed quality/reconciliation job as a data incident, not only an application incident.
- Preserve the failing source file and job output.
- Do not use `WRITE_TRUNCATE` in production unless the recovery procedure explicitly requires it.
- Re-run quality and reconciliation checks after correction and confirm the dashboard returns to normal.

## 6. Recovery checklist

- [ ] Root cause identified or mitigated.
- [ ] Failed events/jobs have succeeded on retry or were safely replayed.
- [ ] BigQuery quality and reconciliation checks pass.
- [ ] Cloud Monitoring alerts are clear.
- [ ] Incident notes include request IDs, revision and source objects involved.
