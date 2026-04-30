# status-banner

Full-width status ribbon at the top of a document — DRAFT, FOR REVIEW, FINAL, CONFIDENTIAL — used to flag a document's lifecycle state at a glance.

## Inputs

| Field | Required | Description |
|---|---|---|
| `label` | yes | Short uppercase label rendered in the centre of the ribbon (e.g. `DRAFT`, `FOR REVIEW`, `FINAL`). Caller controls casing. |
| `tone` | no | One of `info` (default), `warn`, `success`, `danger`, `neutral`. |
| `sublabel` | no | Optional smaller text on the trailing side (e.g. revision number, reviewer initials, expiry date). |

## Tone guidance

- `info` — neutral / informational (default)
- `warn` — DRAFT, FOR REVIEW, NEEDS APPROVAL
- `success` — FINAL, APPROVED, ISSUED
- `danger` — RECALLED, SUPERSEDED, DO NOT USE
- `neutral` — CONFIDENTIAL, INTERNAL ONLY

## Example

```yaml
- component: status-banner
  inputs:
    label: "DRAFT"
    tone: warn
    sublabel: "Rev 0.3 · awaiting board approval"
```
