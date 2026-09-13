# QCSTS Specification Engine

## Purpose
Replace free-text/implicit result evaluation with deterministic, versioned acceptance rules.

## Rule types
- Range
- NLT
- NMT
- Explicit target + explicit tolerance
- Exact where scientifically appropriate
- Boolean
- Enumeration
- Qualitative/textual criteria

## Specification fields
```text
parameter
data_type
unit
rule_type
lower_limit
upper_limit
target
tolerance
precision
rounding_rule
acceptance_rule
effective_from
effective_to
version
```

## Evaluation pipeline
```text
Raw input
 -> syntax validation
 -> normalization
 -> unit validation/conversion
 -> load SpecificationVersion
 -> deterministic calculation
 -> acceptance evaluation
 -> Pass/Fail/Invalid
 -> persist evidence
 -> audit
```

## Critical rule
Never invent scientific tolerance. In particular, do not apply an implicit 2% tolerance to an exact-looking number unless explicitly configured by the approved specification.

## Invalid vs fail
Malformed/unparseable input is an invalid data-entry condition, not automatically a scientific failure.

## Calculation evidence
For calculated values, persist inputs, formula/rule version and output sufficient to reproduce the decision.

## Version binding
Submitted results reference the exact SpecificationVersion and retain a canonical snapshot/hash.

## Units
Store observed unit and normalized unit separately. Reject incompatible units rather than silently guessing conversions.

## Acceptance criteria
- same inputs/version always produce same outcome
- no hidden coercion
- no implicit tolerance
- historical results remain reproducible
- all supported rule types have automated tests
