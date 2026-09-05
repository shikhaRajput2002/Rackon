import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";
import { AdvisorIcon, ArrowLeftIcon, CheckIcon, CompassIcon, UserIcon, WalletIcon } from "../components/icons";
import { Button, Card, Field, Input, Loading, Select, Textarea } from "../components/ui";

const EMPLOYMENT = [
  ["SALARIED", "Salaried"],
  ["SELF_EMPLOYED", "Self-employed"],
  ["STUDENT", "Student"],
  ["BETWEEN_JOBS", "Between jobs"],
];

const RISK = [
  ["LOW", "Cautious — I want the safe option"],
  ["MEDIUM", "Balanced"],
  ["HIGH", "Comfortable with risk"],
];

const CURRENCIES = [
  ["INR", "₹  Indian rupee"],
  ["USD", "$  US dollar"],
  ["EUR", "€  Euro"],
  ["GBP", "£  Pound sterling"],
];

const SYMBOLS = { INR: "₹", USD: "$", EUR: "€", GBP: "£" };

const trimDecimals = (value) =>
  typeof value === "string" && /^-?\d+\.\d+$/.test(value) ? String(Number(value)) : value;

const FIELDS = [
  "age",
  "city",
  "dependents",
  "employment_type",
  "currency",
  "monthly_income",
  "monthly_expenses",
  "current_savings",
  "existing_emi",
  "risk_appetite",
  "goals",
];

export default function Profile() {
  const navigate = useNavigate();
  // Whoever sent us here says where to go back to. The advisor also passes the
  // question it could not answer, so it can be waiting when you return.
  const { returnTo = "/", pendingQuestion } = useLocation().state || {};

  const [form, setForm] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api("/profile/").then((profile) => {
      const next = {};
      FIELDS.forEach((key) => {
        // The API sends decimals as "120000.00"; a form field should just say 120000.
        const value = profile[key];
        next[key] = value === null || value === undefined ? "" : trimDecimals(value);
      });
      setForm(next);
    });
  }, []);

  if (!form) return <Loading />;

  const symbol = SYMBOLS[form.currency] || "";
  const update = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    const payload = {};
    FIELDS.forEach((key) => {
      payload[key] = form[key] === "" ? null : form[key];
    });
    ["city", "goals"].forEach((key) => {
      payload[key] = form[key] || "";
    });
    await api("/profile/", { method: "PATCH", body: payload });
    navigate(returnTo, { state: pendingQuestion ? { pendingQuestion } : undefined });
  }

  const returningToAsk = returnTo === "/ask";

  return (
    <form onSubmit={submit} className="mx-auto max-w-2xl space-y-6">
      <header>
        {returningToAsk && (
          <button
            type="button"
            onClick={() => navigate(returnTo)}
            className="mb-4 flex items-center gap-1.5 text-sm text-mute transition hover:text-soft"
          >
            <ArrowLeftIcon width={15} height={15} />
            Back to your question
          </button>
        )}
        <h1 className="serif text-2xl text-paper">Your details</h1>
        <p className="mt-2 max-w-xl text-sm leading-relaxed text-mute">
          The advisor works out what a purchase does to your month using these figures. Rough is fine —
          round numbers beat blank ones. Nothing here leaves your machine.
        </p>
      </header>

      {returningToAsk && pendingQuestion && (
        <Card className="border-accent/25 bg-accent/[0.05] p-4">
          <div className="flex items-start gap-2.5">
            <AdvisorIcon width={16} height={16} className="mt-0.5 shrink-0 text-accent" />
            <p className="text-sm leading-relaxed text-soft">
              Waiting on: <span className="text-paper">&ldquo;{pendingQuestion}&rdquo;</span> — fill these in
              and you will land back on it.
            </p>
          </div>
        </Card>
      )}

      <Section Icon={UserIcon} title="About you" blurb="Context for anything that is not purely arithmetic.">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Age">
            <Input type="number" min="14" max="110" value={form.age} onChange={update("age")} placeholder="29" />
          </Field>
          <Field label="City">
            <Input value={form.city} onChange={update("city")} placeholder="Bengaluru" />
          </Field>
          <Field label="People who depend on you" hint="Count yourself if nobody else does.">
            <Input type="number" min="0" max="20" value={form.dependents} onChange={update("dependents")} />
          </Field>
          <Field label="Work">
            <Select value={form.employment_type} onChange={update("employment_type")}>
              {EMPLOYMENT.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </Select>
          </Field>
        </div>
      </Section>

      <Section
        Icon={WalletIcon}
        title="Money"
        blurb="Monthly figures, after tax. These four do all the work."
        required
      >
        <Field label="Currency">
          <Select value={form.currency} onChange={update("currency")}>
            {CURRENCIES.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Money
            label="Monthly income"
            hint="What actually lands in your account."
            symbol={symbol}
            required
            value={form.monthly_income}
            onChange={update("monthly_income")}
            placeholder="120000"
          />
          <Money
            label="Monthly expenses"
            hint="Rent, food, bills — your living costs."
            symbol={symbol}
            required
            value={form.monthly_expenses}
            onChange={update("monthly_expenses")}
            placeholder="65000"
          />
          <Money
            label="Savings"
            hint="What you could reach this week if you had to."
            symbol={symbol}
            required
            step="10000"
            value={form.current_savings}
            onChange={update("current_savings")}
            placeholder="600000"
          />
          <Money
            label="Existing EMIs"
            hint="Loan payments you are already committed to, monthly."
            symbol={symbol}
            value={form.existing_emi}
            onChange={update("existing_emi")}
            placeholder="12000"
          />
        </div>
      </Section>

      <Section Icon={CompassIcon} title="How you weigh things" blurb="Used when there is no arithmetic to run.">
        <Field label="When money is on the line">
          <Select value={form.risk_appetite} onChange={update("risk_appetite")}>
            {RISK.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="What you are working toward" hint="Purchases get weighed against this.">
          <Textarea
            rows={3}
            value={form.goals}
            onChange={update("goals")}
            placeholder="Six months of runway before I try anything on my own."
          />
        </Field>
      </Section>

      <div className="sticky bottom-6 flex flex-wrap items-center gap-3 rounded-xl border border-line bg-surface/95 p-3 backdrop-blur">
        <Button type="submit" disabled={busy}>
          <span className="flex items-center gap-1.5">
            <CheckIcon width={15} height={15} />
            {busy ? "Saving…" : returningToAsk ? "Save and go back to your question" : "Save details"}
          </span>
        </Button>
        <Button type="button" variant="ghost" onClick={() => navigate(returnTo)}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

function Section({ Icon, title, blurb, required, children }) {
  return (
    <Card className="p-6">
      <div className="mb-5 flex items-start gap-3 border-b border-line pb-4">
        <span className="mt-0.5 shrink-0 rounded-lg border border-line bg-raised p-1.5 text-accent">
          <Icon width={17} height={17} />
        </span>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="font-medium text-paper">{title}</h2>
            {required && (
              <span className="rounded-full border border-accent/30 bg-accent/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-accent">
                Needed for advice
              </span>
            )}
          </div>
          <p className="mt-0.5 text-sm text-mute">{blurb}</p>
        </div>
      </div>
      <div className="space-y-5">{children}</div>
    </Card>
  );
}

function Money({ label, hint, symbol, value, onChange, placeholder, required, step = "1000" }) {
  return (
    <Field label={label} hint={hint}>
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-mute">
          {symbol}
        </span>
        <input
          type="number"
          min="0"
          step={step}
          required={required}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="w-full rounded-lg border border-line bg-raised py-2.5 pl-8 pr-3 text-sm tabular-nums text-paper placeholder:text-mute/60 outline-none focus:border-accent/60"
        />
      </div>
    </Field>
  );
}
