# <center> QC Stability Tracking System v0.1.3</center>
<center>
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev)
[![GMP](https://img.shields.io/badge/GMP-Compliant-brightgreen.svg)](https://www.fda.gov/drugs/pharmaceutical-quality-resources/good-manufacturing-practice-gmp-resources)
[![21 CFR Part 11](https://img.shields.io/badge/21%20CFR%20Part%2011-Compliant-blue.svg)](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application)</center>

> **Enterprise pharmaceutical quality control platform** for GMP stability studies, chamber inventory management, sample pull workflows with quantity confirmation, and 21 CFR Part 11 compliant test result entry with auto pass/fail calculation.

---

## Overview

QC Stability Tracking System is designed to support pharmaceutical stability studies by providing a structured, auditable workflow for batch lifecycle management, chamber placement, sample pull tracking, test entry, and result review. It supports regulated environments and helps ensure consistency with industry expectations.

## Key Features

- Batch creation and study scheduling based on incubation dates
- Chamber inventory management with unique shelf/rack/position validation
- Sample pull workflow with quantity confirmation and status tracking
- Test result entry with auto pass/fail evaluation against specification limits
- Review and approval workflow for controlled release of data
- Report generation for regulatory and GMP documentation

## Supported Stability Study Types

| Study Type | Time Points | Typical Conditions |
|------------|-------------|--------------------|
| Long-term | 0M, 3M, 6M, 9M, 12M, 18M, 24M, 36M | 25°C / 60% RH |
| Accelerated | 0M, 3M, 6M | 40°C / 75% RH |

## Architecture

This repository includes both backend and frontend components:

- `QCSTS/` - Django backend, REST API, database models, authentication, and workflow logic
- `QCSTS_frontend/` - React and Vite frontend for user interaction and study management

## Installation

1. Clone the repository
2. Configure the Python environment using the backend requirements
3. Set up the database and migrate models
4. Install frontend dependencies and run the React app

> See `QCSTS/requirements.txt`, `QCSTS/pyproject.toml`, and `QCSTS_frontend/package.json` for dependency details.

## Getting Started

1. Activate the backend environment and install dependencies
2. Run Django migrations: `python manage.py migrate`
3. Start the backend server: `python manage.py runserver`
4. Install frontend dependencies in `QCSTS_frontend/`
5. Run the frontend development server with `npm install` and `npm run dev`

## Testing

Backend tests are available in the Django app directories under `QCSTS/apps/*/tests/`. Use the configured test runner and `pytest` where applicable.

## Documentation

Project documentation and additional notes are available in the repository, including API documentation in `QCSTS/API_DOCUMENTATION.md`.

## Contribution

Contributions should follow existing application structure, maintain code quality, and preserve testing coverage. Use the current repository conventions for apps, serializers, views, and migration management.

## License

This project is provided under the license terms defined in [LICENSE.md](LICENSE.md).

