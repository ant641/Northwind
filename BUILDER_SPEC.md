# Builder spec: Northwind support-ticket auto-triage

## Scope
Read the Q1 ticket export, validate its schema, deterministically route low-risk repetitive categories, retain all other tickets for human review, and emit a row-level audit file plus a before-to-after workload summary.

## Data contract
Input: `support_tickets_q1_2026.csv`.
Required columns: `Ticket_ID`, `Date`, `Category`, `Submitted_By`, `Assigned_To`, `Handle_Minutes`, `Status`.
`Ticket_ID` must be unique; `Handle_Minutes` must be a non-negative integer; `Status` is preserved, never changed by the automation.

## Rules
- `Thumbnail re-upload` -> `AUTO_RESOLVE`; modeled after-time 5 minutes.
- `Login issue` -> `AUTO_RESOLVE`; modeled after-time 3 minutes.
- `Account access` -> `AUTO_RESOLVE`; modeled after-time 5 minutes.
- Every other category -> `HUMAN_REVIEW`; after-time equals source `Handle_Minutes`.

The modeled after-times are pilot assumptions. They are intentionally explicit and must not be represented as observed savings.

## Outputs
- `output/routed_tickets.csv`: source columns plus action, estimated after-minutes and estimated minutes saved.
- `output/summary.json`: ticket count, baseline minutes, modeled after-minutes, modeled minutes saved and reduction percentage.

## Answer-complete acceptance test
Running `python automate_support.py support_tickets_q1_2026.csv output` succeeds only when the required schema is exact; preserves every input row and source field; creates both output files; routes only allow-listed categories automatically; leaves all other categories for human review; and reconciles baseline and after-minutes exactly to the row-level output.

## In
CSV validation, deterministic classification, queue routing, row-level auditability, workload arithmetic.

## Out
Sending creator messages, changing ticket status, tax or payout decisions, identity verification, production-system writes, and claiming realized savings before a timed pilot.
