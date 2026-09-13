# Result Engine

## Purpose

Provide deterministic and auditable laboratory result handling.

## Pipeline

```text
Raw input
 -> validation
 -> normalization
 -> unit validation
 -> specification lookup
 -> calculation
 -> acceptance evaluation
 -> result state
 -> audit
```

## Result states

Draft/Prepared -> Submitted -> Under Review -> Approved/Rejected -> Superseded.

## No hidden coercion

Do not silently strip characters, guess units or invent tolerance. Normalization rules must be explicit.

## Calculation record

When a result depends on a calculation, retain the inputs, formula/rule version and output.

## Corrections

Original submitted results remain immutable. Corrections create linked records.

## Acceptance criteria

- deterministic result evaluation
- reproducible historical result
- no arbitrary exact-value tolerance
- failed parsing is classified as invalid input, not as scientific failure
