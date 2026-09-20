"use client";

import { useEffect, useState } from "react";
import { api, endpoints, type ApiEnvelope } from "@/lib/api";
import type { Organization } from "@/lib/auth";

type Plan = {
  id: string;
  code: string;
  name: string;
  description: string;
  monthly_price: string | number;
  annual_price: string | number;
  currency: string;
  max_users?: number | null;
  max_sites?: number | null;
  max_studies?: number | null;
  max_storage_mb?: number | null;
  api_access?: boolean;
  active: boolean;
};

type Subscription = {
  id: string;
  status: string;
  interval: string;
  provider: string;
  trial_ends_at?: string | null;
  current_period_start?: string | null;
  current_period_end?: string | null;
  cancel_at_period_end?: boolean;
  plan: Plan;
};

type Usage = {
  id: string;
  metric: string;
  period_start: string;
  period_end: string;
  quantity: number;
};

function listOf<T>(data: T[] | { results?: T[] } | null | undefined): T[] {
  if (Array.isArray(data)) return data;
  return data?.results || [];
}

export default function BillingPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [usage, setUsage] = useState<Usage[]>([]);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");

    try {
      const [planResponse, subscriptionResponse, usageResponse] = await Promise.all([
        api<ApiEnvelope<Plan[] | { results?: Plan[] }>>(endpoints.plans),
        api<ApiEnvelope<Subscription[] | { results?: Subscription[] }>>(endpoints.billing),
        api<ApiEnvelope<Usage[] | { results?: Usage[] }>>(endpoints.usage),
        api<ApiEnvelope<Organization[] | { results?: Organization[] }>>(endpoints.organizations),
      ]);

      const planList = listOf(planResponse.data);
      const subscriptionList = listOf(subscriptionResponse.data);
      setPlans(planList);
      setSubscription(subscriptionList[0] || null);
      setUsage(listOf(usageResponse.data));
      const organizations = listOf(organizationResponse.data);
      setOrganization(organizations[0] || null);
    } catch (value) {
      setError(value instanceof Error ? value.message : "Unable to load billing data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  return (
    <div className="content">
      <div className="page-header">
        <div>
          <span className="eyebrow">SUBSCRIPTION</span>
          <h1>Billing & usage</h1>
          <p>Live subscription, plan catalog and usage data from the QCSTS billing API.</p>
        </div>
        <button className="btn" onClick={() => void load()} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && <div className="inline-error">{error}</div>}

      <section className="stats three">
        <div className="stat-card">
          <span>Organization</span>
          <strong>{organization?.name || "—"}</strong>
          <small>{organization?.currency || "—"} · {organization?.country || "—"}</small>
        </div>
        <div className="stat-card">
          <span>Current plan</span>
          <strong>{subscription?.plan?.name || (loading ? "—" : "No active plan")}</strong>
          <small>{subscription?.status || "—"}</small>
        </div>
        <div className="stat-card">
          <span>Billing interval</span>
          <strong>{subscription?.interval || "—"}</strong>
          <small>{subscription?.current_period_end ? "Renews " + new Date(subscription.current_period_end).toLocaleDateString() : "—"}</small>
        </div>
      </section>

      <section className="card table-card">
        <div className="card-header">
          <div><strong>Available plans</strong><span>{plans.length} active plans</span></div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Plan</th><th>Monthly</th><th>Annual</th><th>Users</th><th>Sites</th><th>Studies</th><th>API</th></tr></thead>
            <tbody>
              {plans.map((plan) => (
                <tr key={plan.id}>
                  <td><b>{plan.name}</b><div className="muted">{plan.description}</div></td>
                  <td>{plan.currency} {plan.monthly_price}</td>
                  <td>{plan.currency} {plan.annual_price}</td>
                  <td>{plan.max_users ?? "Unlimited"}</td>
                  <td>{plan.max_sites ?? "Unlimited"}</td>
                  <td>{plan.max_studies ?? "Unlimited"}</td>
                  <td>{plan.api_access ? "Enabled" : "Not included"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!plans.length && !loading && <div className="empty">No active plans were returned by the backend.</div>}
        </div>
      </section>

      <section className="card table-card">
        <div className="card-header">
          <div><strong>Usage</strong><span>{usage.length} usage records</span></div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Metric</th><th>Quantity</th><th>Period start</th><th>Period end</th></tr></thead>
            <tbody>
              {usage.map((item) => (
                <tr key={item.id}>
                  <td><b>{item.metric}</b></td>
                  <td>{item.quantity}</td>
                  <td>{new Date(item.period_start).toLocaleDateString()}</td>
                  <td>{new Date(item.period_end).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!usage.length && !loading && <div className="empty">No usage records returned for this organization.</div>}
        </div>
      </section>

      <section className="card detail-card">
        <h3>Payment processing</h3>
        <p>
          The current backend exposes subscription and usage data, but payment provider checkout/webhooks
          are not part of this API surface yet. This screen therefore does not pretend that plan upgrades
          or payments are connected.
        </p>
      </section>
    </div>
  );
}
