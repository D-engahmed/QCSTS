# Specifications

## Purpose

Specifications define acceptance criteria for laboratory tests.

## Principle

Do not infer scientific acceptance criteria from arbitrary user input or generic assumptions.

## Supported rule types

- range
- NLT
- NMT
- target with explicitly defined tolerance
- exact value where exactness is truly intended
- boolean
- enumerated text
- qualitative/text criteria

## Fields

- parameter
- data type
- unit
- rule type
- lower limit
- upper limit
- target
- tolerance
- precision
- rounding rule
- acceptance rule
- effective dates

## Determinism

Evaluation must produce the same outcome from the same normalized value, unit and specification version.

## Acceptance criteria

The system must reject ambiguous or unsupported specification formats rather than silently treating them as failed scientific results.
