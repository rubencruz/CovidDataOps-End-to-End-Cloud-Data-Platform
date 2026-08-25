# Phase 7 — Production

Phase 7 adds the operational controls required to run the pipeline continuously in production while preserving the Phase 4 event-driven and Phase 5 scheduled execution paths.

## Production controls

- **Observability:** Cloud Run requests emit structured JSON logs with request IDs, release version, revision, duration and source object metadata.
- **Monitoring:** a Cloud Monitoring dashboard covers request rate, p99 latency, application errors and data-quality failures.
- **Alerting:** Cloud Run 5xx rate, application error logs and failed quality/reconciliation jobs can trigger email notifications.
- **Retries:** Cloud Scheduler retains explicit retry policies; Eventarc/Pub/Sub delivery continues to use HTTP failure semantics, so transient application failures return 500 and can be redelivered.
- **Data quality:** Phase 5 quality and reconciliation jobs remain scheduled and are promoted to monitored production signals.
- **CI/CD:** GitHub Actions validates Python and Terraform on pull requests/pushes and provides a manual production deployment workflow using GitHub OIDC/WIF rather than static GCP keys.
- **Runbook:** operational response steps are documented in `runbooks/production.md`.

## Deployment

Set GitHub environment variables `GCP_PROJECT`, `REGION`, and `NOTIFICATION_EMAIL`, plus secrets `GCP_WORKLOAD_IDENTITY_PROVIDER` and `GCP_DEPLOYER_SERVICE_ACCOUNT`. Run the `Deploy production` workflow and supply a release tag.

For manual deployment:

```bash
PROJECT_ID=your-project REGION=us-central1 ./scripts/deploy.sh
```

The deployment script builds `:phase-7`, applies Terraform and passes the release version into Cloud Run.

## Alert configuration

`notification_email` is optional. When set, Terraform creates an email notification channel and attaches it to the production policies. When empty, policies remain active in Cloud Monitoring but do not send email notifications.
