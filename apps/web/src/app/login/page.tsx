"use client";

import { Building2, ShieldCheck, Workflow, Wrench } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ApiError, authApi } from "@/lib/api";
import type { AuthProviderStatus } from "@/lib/types";

export default function LoginPage() {
  const { login, token } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [providers, setProviders] = useState<AuthProviderStatus[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingProviders, setIsLoadingProviders] = useState(true);

  useEffect(() => {
    if (token) {
      router.replace("/dashboard");
    }
  }, [router, token]);

  useEffect(() => {
    authApi
      .providers()
      .then((response) => {
        setProviders(response);
      })
      .catch(() => {
        setProviders([{ key: "password", label: "Email and password", enabled: true }]);
      })
      .finally(() => {
        setIsLoadingProviders(false);
      });
  }, []);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message);
      } else {
        setError("Unexpected error while signing in.");
      }
      setIsSubmitting(false);
    }
  };

  const microsoftProvider = providers.find((provider) => provider.key === "microsoft");
  const canUseMicrosoft = microsoftProvider?.enabled ?? false;

  return (
    <main className="grid min-h-screen gap-8 px-6 py-8 lg:grid-cols-[1.15fr_0.85fr] lg:px-10">
      <section className="rounded-[2rem] bg-ink px-8 py-10 text-white shadow-panel lg:px-12 lg:py-14">
        <p className="text-xs uppercase tracking-[0.3em] text-white/45">Operations AI MVP</p>
        <h1 className="mt-6 max-w-xl text-4xl font-semibold leading-tight lg:text-5xl">
          Internal knowledge, reporting, and workflow support for operations teams.
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-8 text-white/68">
          Search SOPs and policies with citations, generate weekly reports for leadership, and
          automate routine operational follow-up without building a heavyweight platform first.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {[
            {
              icon: ShieldCheck,
              title: "Cited answers",
              description: "Ground responses in uploaded procedures and policies."
            },
            {
              icon: Wrench,
              title: "Ops reporting",
              description: "Turn raw updates into executive and operational summaries."
            },
            {
              icon: Workflow,
              title: "Rules-based actions",
              description: "Trigger summaries, flags, and notifications from business rules."
            }
          ].map(({ icon: Icon, title, description }) => (
            <div key={title} className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <Icon className="h-5 w-5 text-white/80" />
              <h2 className="mt-5 text-lg font-semibold">{title}</h2>
              <p className="mt-3 text-sm leading-6 text-white/58">{description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="flex items-center">
        <Card className="mx-auto w-full max-w-xl p-8 lg:p-10">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate">
              Sign in
            </p>
            <h2 className="mt-4 text-3xl font-semibold text-ink">Access your workspace</h2>
            <p className="mt-4 text-sm leading-7 text-slate">
              Use a local development account or sign in with Microsoft Entra ID when configured.
            </p>
          </div>

          {canUseMicrosoft ? (
            <div className="mt-8">
              <Button
                className="w-full"
                onClick={() => {
                  window.location.href = authApi.microsoftStartUrl("/dashboard");
                }}
                type="button"
                variant="secondary"
              >
                <Building2 className="mr-2 h-4 w-4" />
                Continue with Microsoft
              </Button>
              <p className="mt-3 text-xs text-slate">
                Organizational sign-in is enabled for this workspace.
              </p>
            </div>
          ) : null}

          {!isLoadingProviders ? (
            <div className="mt-6 flex items-center gap-3 text-xs uppercase tracking-[0.22em] text-slate/70">
              <span className="h-px flex-1 bg-edge" />
              <span>Local access</span>
              <span className="h-px flex-1 bg-edge" />
            </div>
          ) : null}

          <form className="mt-8 space-y-5" onSubmit={onSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">Email</label>
              <Input
                placeholder="you@company.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-ink">Password</label>
              <Input
                placeholder="Enter your password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>

            {error ? (
              <div className="rounded-2xl border border-alert/20 bg-alert/5 px-4 py-3 text-sm text-alert">
                {error}
              </div>
            ) : null}

            <Button className="w-full" disabled={isSubmitting} type="submit">
              {isSubmitting ? "Signing in..." : "Enter workspace"}
            </Button>
          </form>

          <div className="mt-8 rounded-2xl border border-edge bg-mist p-4 text-sm text-slate">
            Local development users:
            <div className="mt-2 font-[var(--font-mono)] text-xs text-ink">
              admin@ops-ai-demo.example.com / AdminPass123!
            </div>
            <div className="mt-1 font-[var(--font-mono)] text-xs text-ink">
              analyst@ops-ai-demo.example.com / UserPass123!
            </div>
          </div>
        </Card>
      </section>
    </main>
  );
}
