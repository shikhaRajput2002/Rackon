import { useState } from "react";
import { useAuth } from "../auth";
import { AdvisorIcon, ChartIcon, LedgerIcon, LockIcon } from "../components/icons";
import { Button, Field, Input } from "../components/ui";

// The app's voice, on the front door. No invented statistics — the reply is
// about the person holding the slider, not a study.
const REPLIES = [
  { at: 0, line: "Then why are you about to do it?" },
  { at: 20, line: "Refreshingly honest. Most people never say this out loud." },
  { at: 40, line: "A coin flip you will nonetheless defend for twenty minutes." },
  { at: 60, line: "This is where almost everyone sits. It is also where almost everyone is wrong." },
  { at: 80, line: "Confident. Now name the one thing that would change your mind." },
  { at: 93, line: "Nobody is this sure. Not about anything worth writing down." },
];

const STEPS = [
  { Icon: LedgerIcon, label: "Log it", detail: "with a number" },
  { Icon: AdvisorIcon, label: "Be challenged", detail: "the case against" },
  { Icon: LockIcon, label: "Lock it", detail: "no edits after" },
  { Icon: ChartIcon, label: "Score it", detail: "months later" },
];

const replyFor = (value) => [...REPLIES].reverse().find((reply) => value >= reply.at).line;

export default function Login() {
  const { login, register } = useAuth();
  const [isRegistering, setIsRegistering] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const [confidence, setConfidence] = useState(78);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const update = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (isRegistering) {
        await register(form.email, form.password, form.name);
      } else {
        await login(form.email, form.password);
      }
    } catch (caught) {
      setError(caught.message);
      setBusy(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* A quiet chart grid — the surface everything in this app is eventually plotted on. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-y-0 left-0 w-full lg:w-[58%]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to bottom, var(--color-paper) 0 1px, transparent 1px 44px)",
          opacity: 0.028,
          maskImage: "linear-gradient(to right, black 55%, transparent 100%)",
          WebkitMaskImage: "linear-gradient(to right, black 55%, transparent 100%)",
        }}
      />

      <div className="relative mx-auto grid min-h-screen max-w-6xl items-center gap-12 px-6 py-14 lg:grid-cols-[1.15fr_1fr] lg:gap-16 lg:py-20">
        <section className="order-2 lg:order-1">
          <p className="serif text-lg tracking-tight text-paper">Reckon</p>

          <p className="mt-10 text-[11px] font-medium uppercase tracking-[0.18em] text-mute">
            Before you sign in
          </p>
          <h1 className="serif mt-3 max-w-lg text-[2.6rem] leading-[1.06] tracking-tight text-paper sm:text-5xl">
            How sure are you that you&rsquo;re usually right?
          </h1>

          <div className="mt-9 max-w-lg">
            <div className="flex items-end gap-3">
              <span className="text-6xl font-semibold leading-none tabular-nums text-accent">{confidence}</span>
              <span className="pb-1.5 text-2xl text-mute">%</span>
            </div>

            <input
              type="range"
              min="0"
              max="100"
              value={confidence}
              aria-label="How sure are you that you are usually right?"
              onChange={(event) => setConfidence(Number(event.target.value))}
              className="mt-5 w-full"
            />

            <p className="mt-4 min-h-[3.25rem] text-[15px] leading-relaxed text-soft">
              {replyFor(confidence)}
            </p>
          </div>

          <div className="mt-9 max-w-lg border-t border-line pt-7">
            <p className="text-[15px] leading-relaxed text-soft">
              Reckon is a decision journal that keeps that number honest. You write down what you expect
              <span className="text-paper"> before </span>
              you know the answer — then it locks, and comes back later to ask how it went.
            </p>

            <ul className="mt-6 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
              {STEPS.map(({ Icon, label, detail }) => (
                <li key={label}>
                  <Icon width={17} height={17} className="text-accent" />
                  <p className="mt-2 text-sm font-medium text-paper">{label}</p>
                  <p className="mt-0.5 text-xs leading-snug text-mute">{detail}</p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="order-1 lg:order-2">
          <form
            onSubmit={submit}
            className="w-full rounded-2xl border border-line bg-surface p-7 sm:p-8 lg:ml-auto lg:max-w-sm"
          >
            <h2 className="serif text-xl text-paper">{isRegistering ? "Create an account" : "Sign in"}</h2>
            <p className="mt-1.5 text-sm text-mute">
              {isRegistering ? "It takes about fifteen seconds." : "Welcome back."}
            </p>

            <div className="mt-6 space-y-4">
              {isRegistering && (
                <Field label="Name">
                  <Input value={form.name} onChange={update("name")} placeholder="Optional" />
                </Field>
              )}
              <Field label="Email">
                <Input
                  type="email"
                  required
                  autoComplete="email"
                  value={form.email}
                  onChange={update("email")}
                  placeholder="you@example.com"
                />
              </Field>
              <Field label="Password" hint={isRegistering ? "At least 8 characters." : null}>
                <Input
                  type="password"
                  required
                  autoComplete={isRegistering ? "new-password" : "current-password"}
                  value={form.password}
                  onChange={update("password")}
                  placeholder="••••••••"
                />
              </Field>
            </div>

            {error && <p className="mt-4 text-sm text-bad">{error}</p>}

            <Button type="submit" disabled={busy} className="mt-6 w-full">
              {busy ? "Just a moment…" : isRegistering ? "Create account" : "Sign in"}
            </Button>

            <button
              type="button"
              onClick={() => setIsRegistering(!isRegistering)}
              className="mt-4 w-full text-sm text-mute transition hover:text-soft"
            >
              {isRegistering ? "I already have an account" : "Create an account"}
            </button>

            <div className="mt-6 border-t border-line pt-5">
              <button
                type="button"
                onClick={() => {
                  setForm({ email: "demo@reckon.local", password: "reckon123", name: "" });
                  setIsRegistering(false);
                  setError(null);
                }}
                className="group w-full text-left transition hover:opacity-80"
              >
                <span className="flex items-center gap-2 text-sm text-accent">
                  Use the demo account
                  <span aria-hidden="true" className="transition group-hover:translate-x-0.5">&rarr;</span>
                </span>
                <span className="mt-1 block text-xs leading-snug text-mute">
                  A year of scored decisions, and a 13-point confidence problem
                </span>
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
