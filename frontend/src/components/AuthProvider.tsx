"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, endpoints, type ApiEnvelope, type AuthResponse, type RegistrationInput } from "@/lib/api";
import { authStorage } from "@/lib/auth";
import type { User, Organization, Site, Membership } from "@/lib/auth";

type AuthContextValue = {
  user: User | null;
  organizations: Organization[];
  sites: Site[];
  membership: Membership | null;
  organization: Organization | null;
  site: Site | null;
  loading: boolean;
  login: (email: string, password: string, otp?: string) => Promise<void>;
  register: (input: RegistrationInput) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function applyAuthResponse(response: AuthResponse) {
  authStorage.setSession(response.access, response.refresh, response.user, {
    organization: response.organization,
    site: response.site,
    membership: response.membership,
  });
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(authStorage.user);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);

  const loadSession = async () => {
    if (!authStorage.access) {
      setLoading(false);
      return;
    }

    try {
      const me = await api<ApiEnvelope<User>>(endpoints.me);
      setUser(me.data);
      authStorage.setUser(me.data);

      const orgResponse = await api<ApiEnvelope<Organization[]>>(endpoints.organizations);
      const orgList = orgResponse.data ?? [];
      setOrganizations(orgList);

      const activeOrganization =
        orgList.find((item) => item.id === authStorage.organizationId) ?? orgList[0] ?? null;

      if (!activeOrganization) {
        authStorage.setOrganization(null);
        authStorage.setSite(null);
        setSites([]);
        return;
      }

      authStorage.setOrganization(activeOrganization.id);

      const siteResponse = await api<ApiEnvelope<Site[]>>(endpoints.sites, {
        organizationId: activeOrganization.id,
      });
      const siteList = siteResponse.data ?? [];
      setSites(siteList);

      const activeSite =
        siteList.find((item) => item.id === authStorage.siteId) ?? siteList[0] ?? null;
      authStorage.setSite(activeSite?.id ?? null);
    } catch {
      authStorage.clear();
      setUser(null);
      setOrganizations([]);
      setSites([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadSession();
  }, []);

  const login = async (email: string, password: string, otp?: string) => {
    const response = await api<ApiEnvelope<AuthResponse>>(endpoints.login, {
      method: "POST",
      body: JSON.stringify({ email, password, ...(otp ? { otp } : {}) }),
      skipRefresh: true,
    });

    applyAuthResponse(response.data);
    setUser(response.data.user);

    const orgResponse = await api<ApiEnvelope<Organization[]>>(endpoints.organizations, {
      token: response.data.access,
    });
    const orgList = orgResponse.data ?? [];
    setOrganizations(orgList);

    const activeOrganization = response.data.organization ?? orgList[0] ?? null;
    if (activeOrganization) {
      authStorage.setOrganization(activeOrganization.id);
      const siteResponse = await api<ApiEnvelope<Site[]>>(endpoints.sites, {
        token: response.data.access,
        organizationId: activeOrganization.id,
      });
      const siteList = siteResponse.data ?? [];
      setSites(siteList);
      const activeSite = response.data.site ?? siteList[0] ?? null;
      authStorage.setSite(activeSite?.id ?? null);
    } else {
      authStorage.setOrganization(null);
      authStorage.setSite(null);
      setSites([]);
    }
  };

  const register = async (input: RegistrationInput) => {
    const response = await api<ApiEnvelope<AuthResponse>>(endpoints.register, {
      method: "POST",
      body: JSON.stringify(input),
      skipRefresh: true,
    });

    applyAuthResponse(response.data);
    setUser(response.data.user);

    if (response.data.organization) {
      setOrganizations([response.data.organization]);
      authStorage.setOrganization(response.data.organization.id);
    } else {
      setOrganizations([]);
      authStorage.setOrganization(null);
    }

    setSites(response.data.site ? [response.data.site] : []);
    authStorage.setSite(response.data.site?.id ?? null);
  };

  const logout = async () => {
    const refresh = authStorage.refresh;

    try {
      if (refresh && authStorage.access) {
        await api(endpoints.logout, {
          method: "POST",
          body: JSON.stringify({ refresh }),
          skipRefresh: true,
        });
      }
    } finally {
      authStorage.clear();
      setUser(null);
      setOrganizations([]);
      setSites([]);
      window.location.assign("/login");
    }
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      organizations,
      sites,
      membership: authStorage.membership,
      organization:
        organizations.find((item) => item.id === authStorage.organizationId) ?? null,
      site: sites.find((item) => item.id === authStorage.siteId) ?? null,
      loading,
      login,
      register,
      logout,
    }),
    [user, organizations, sites, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
