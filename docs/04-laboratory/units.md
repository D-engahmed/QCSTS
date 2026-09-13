# Units

## Purpose

Provide controlled handling of laboratory units.

## Rules

- each test may define an expected unit or accepted unit family
- conversions must use explicit, tested conversion rules
- the original observed unit remains stored
- normalized unit/value are stored separately

## Acceptance criteria

An invalid or incompatible unit prevents evaluation rather than silently converting to an unrelated unit.
