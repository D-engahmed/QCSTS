"use client";

export type User = {
  id: string;
  email: string;
  full_name: string;
  role?: string | null;
  organization_role?: string | null;
  is_active: boolean;
  created_at: string;
};

export type Organization = {
  id: string;
  name: string;
  legal_name?: string;
  slug: string;
  country: string;
  timezone: string;
  currency: string;
  status: string;
};

export type Site = {
  id: string;
  organization?: string;
  name: string;
  address?: string;
  country?: string;
  timezone?: string;
  status?: string;
};

export type Membership = {
  id: string;
  role: string;
  organization_id: string;
  site_id: string | null;
};

const keys = {
  access: "qc_access_token",
  refresh: "qc_refresh_token",
  user: "qc_user",
  org: "qc_active_organization",
  site: "qc_active_site",
  membership: "qc_membership",
};

export const authStorage = {
  get access() {
    return typeof window === "undefined" ? null : localStorage.getItem(keys.access);
  },
  get refresh() {
    return typeof window === "undefined" ? null : localStorage.getItem(keys.refresh);
  },
  get user(): User | null {
    if (typeof window === "undefined") return null;
    try {
      const value = localStorage.getItem(keys.user);
      return value ? JSON.parse(value) : null;
    } catch {
      return null;
    }
  },
  get organizationId() {
    return typeof window === "undefined" ? null : localStorage.getItem(keys.org);
  },
  get siteId() {
    return typeof window === "undefined" ? null : localStorage.getItem(keys.site);
  },
  get membership(): Membership | null {
    if (typeof window === "undefined") return null;
    try {
      const value = localStorage.getItem(keys.membership);
      return value ? JSON.parse(value) : null;
    } catch {
      return null;
    }
  },

  setSession(
    access: string,
    refresh: string,
    user: User,
    context?: {
      organization?: Organization | null;
      site?: Site | null;
      membership?: Membership | null;
    },
  ) {
    localStorage.setItem(keys.access, access);
    localStorage.setItem(keys.refresh, refresh);
    localStorage.setItem(keys.user, JSON.stringify(user));

    if (context?.organization) {
      this.setOrganization(context.organization.id);
    } else {
      localStorage.removeItem(keys.org);
    }

    if (context?.site) {
      this.setSite(context.site.id);
    } else {
      localStorage.removeItem(keys.site);
    }

    if (context?.membership) {
      localStorage.setItem(keys.membership, JSON.stringify(context.membership));
    } else {
      localStorage.removeItem(keys.membership);
    }
  },

  setUser(user: User) {
    localStorage.setItem(keys.user, JSON.stringify(user));
  },

  setOrganization(id: string | null) {
    if (id) localStorage.setItem(keys.org, id);
    else localStorage.removeItem(keys.org);
  },

  setSite(id: string | null) {
    if (id) localStorage.setItem(keys.site, id);
    else localStorage.removeItem(keys.site);
  },

  clear() {
    Object.values(keys).forEach((key) => localStorage.removeItem(key));
  },
};
