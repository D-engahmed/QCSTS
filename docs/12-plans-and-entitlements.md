# QCSTS Plans and Entitlements

## Commercial status
All prices are launch hypotheses. Store them as data/configuration; never hardcode them in business logic.

## Starter
**$299/month** | **$2,990/year**
Target: small QC teams.

Indicative capacity:
- 1 organization
- 1 site
- 10 users
- 20 active studies
- 500 batches/year
- 5 chambers
- 50 products
- 25 protocols

Included: core stability workflow, scheduling, sample tracking, results, basic QA, signatures, audit trail, basic reports, email notifications, dashboard, MFA.

## Professional — Recommended
**$799/month** | **$7,990/year**
Target: growing pharmaceutical operations.

Indicative capacity:
- 3 sites
- 30 users
- 100 active studies
- 2,500 batches/year
- 20 chambers
- 250 products
- 100 protocols

Adds: advanced analytics/reporting, API, webhooks, advanced notifications, advanced permissions, data export, integration foundation, priority support.

## Business
**$1,499/month** | **$14,990/year**
Target: multi-site organizations.

Indicative capacity:
- 5+ sites
- unlimited users
- unlimited/high study capacity by contract/fair use
- 10,000+ batches/year
- unlimited/high chamber capacity by contract

Adds: SSO, enterprise permissions, advanced integrations, premium support/SLA options, dedicated onboarding.

## Enterprise
Custom pricing. Potential components: dedicated environment/database, private deployment, SSO/SAML, custom security, data residency, retention configuration, LIMS/ERP integrations, validation support, migration, training and SLA.

## Add-ons
Initial hypotheses:
- additional site: +$150/month
- additional 25 users: +$100/month
- additional 50 active studies: +$150/month
- advanced integration: +$250–$750/month
- dedicated environment: +$500–$2,000/month
- data migration: $500–$5,000 one-time
- implementation: $1,500–$10,000+
- validation support: custom

## Entitlement object
Each entitlement should define:
- key
- type (boolean/limit/quantity)
- value
- source plan/add-on/contract
- effective dates

Example:
```json
{
  "key": "active_studies.max",
  "type": "limit",
  "value": 100
}
```

## Usage behavior
At 80–90% capacity warn users. At capacity, prevent creation of additional capacity-consuming resources or require an upgrade/add-on, but never delete historical data or destroy regulated records.

## Annual discount
Target 15–20% effective annual savings. Monthly and annual prices are separate price records linked to the same plan.

## Acceptance criteria
1. Plan changes do not require deployments.
2. Entitlements are centrally enforced server-side.
3. Add-ons compose with base plans.
4. Founding-customer discounts are configuration-driven.
5. Billing failures cannot corrupt regulated records.
6. Historical data remains governed by retention rather than subscription state.
