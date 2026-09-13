# Chambers

## Purpose

Track storage equipment and capacity used for stability studies.

## Required controls

- chamber identity
- site
- target temperature
- target humidity
- capacity
- occupancy
- calibration status
- qualification status
- maintenance status

## Assignment rule

A chamber assignment is permitted only when:
- chamber belongs to active site
- chamber is operational
- calibration/qualification status satisfies protocol policy
- capacity is available

## Acceptance criteria

Invalid chamber assignments are rejected server-side.
