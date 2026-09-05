import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { AdvisorIcon, LedgerIcon, PinIcon, PlusIcon, TrashIcon } from "../components/icons";
import { Button, Card, Loading, Textarea } from "../components/ui";

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

const money = (value, currency = "INR") => {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat(currency === "INR" ? "en-IN" : "en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value);
};

export default function Home() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  const load = useCallback(() => api("/home/").then(setData), []);
  useEffect(() => {
    load();
  }, [load]);

  if (!data) return <Loading />;

  const { profile, quote, track_record: record, reviews_due: due } = data;
  const currency = profile.currency;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="serif text-3xl text-paper">
          {greeting()}
          {data.user.name ? `, ${data.user.name}` : ""}.
        </h1>
        {due > 0 && (
          <p className="mt-2 text-sm text-accent">
            {due} decision{due > 1 ? "s are" : " is"} waiting to be scored.{" "}
            <Link to="/decisions" className="underline decoration-accent/40 underline-offset-4">
              Go and be honest
            </Link>
          </p>
        )}
      </div>

      <Card className="p-7">
        <blockquote className="border-l-2 border-accent/50 pl-5">
          <p className="serif text-xl leading-relaxed text-paper">{quote.text}</p>
          <footer className="mt-3 text-xs uppercase tracking-widest text-mute">{quote.author}</footer>
        </blockquote>
      </Card>

      {profile.is_complete ? (
        <div>
          <p className="mb-3 text-xs font-medium uppercase tracking-wider text-mute">Where you stand</p>
          <div className="grid gap-3 sm:grid-cols-4">
            <Figure label="Monthly income" value={money(profile.monthly_income, currency)} />
            <Figure
              label="Free each month"
              value={money(profile.derived.monthly_disposable, currency)}
              caption="after expenses and EMIs"
              tone="accent"
            />
            <Figure label="Savings" value={money(profile.current_savings, currency)} />
            <Figure
              label="Runway"
              value={profile.derived.emergency_fund_months ? `${profile.derived.emergency_fund_months} mo` : "—"}
              caption="of expenses covered"
            />
          </div>
        </div>
      ) : (
        <Card className="p-6">
          <p className="serif text-lg text-paper">The advisor needs to know a few things first.</p>
          <p className="mt-2 max-w-lg text-sm text-mute">
            Your income, what you spend, and what you have saved. Without those, any answer about whether you
            can afford something is just a guess with confidence.
          </p>
          <Button className="mt-4" onClick={() => navigate("/profile", { state: { returnTo: "/" } })}>
            Fill in your details
          </Button>
        </Card>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        <ActionCard
          to="/ask"
          Icon={AdvisorIcon}
          title="Ask the advisor"
          body="Should I buy the bike? Should I learn to swim? It answers with your actual numbers."
        />
        <ActionCard
          to="/new"
          Icon={LedgerIcon}
          title="Log a decision"
          body={
            record.has_enough_data
              ? `You have been right ${record.accuracy_percent}% of the time. Add another and find out if that holds.`
              : "Write it down before you know the answer. That is the only way this works."
          }
        />
      </div>

      <Notes notes={data.notes} onChange={load} />
    </div>
  );
}

function Figure({ label, value, caption, tone = "paper" }) {
  return (
    <Card className="p-4">
      <p className="text-[11px] font-medium uppercase tracking-wider text-mute">{label}</p>
      <p className={`mt-1.5 text-xl font-semibold tabular-nums ${tone === "accent" ? "text-accent" : "text-paper"}`}>
        {value}
      </p>
      {caption && <p className="mt-1 text-xs text-mute">{caption}</p>}
    </Card>
  );
}

function ActionCard({ to, Icon, title, body }) {
  return (
    <Link to={to} className="block">
      <Card className="h-full p-5 transition hover:border-mute/50">
        <div className="flex items-center gap-2.5">
          <Icon width={18} height={18} className="text-accent" />
          <p className="font-medium text-paper">{title}</p>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-mute">{body}</p>
      </Card>
    </Link>
  );
}

function Notes({ notes, onChange }) {
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);

  async function add(event) {
    event.preventDefault();
    if (!draft.trim() || busy) return;
    setBusy(true);
    const [firstLine, ...rest] = draft.trim().split("\n");
    await api("/notes/", {
      method: "POST",
      body: {
        title: rest.length ? firstLine.slice(0, 200) : "",
        body: rest.length ? rest.join("\n").trim() : firstLine,
      },
    });
    setDraft("");
    await onChange();
    setBusy(false);
  }

  async function togglePin(note) {
    await api(`/notes/${note.uuid}/`, { method: "PATCH", body: { body: note.body, is_pinned: !note.is_pinned } });
    await onChange();
  }

  async function remove(note) {
    await api(`/notes/${note.uuid}/`, { method: "DELETE" });
    await onChange();
  }

  return (
    <div>
      <div className="mb-3 flex items-baseline justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-mute">Notes</p>
        <Link to="/decisions" className="text-xs text-mute transition hover:text-soft">
          Everything else lives in Decisions
        </Link>
      </div>

      <form onSubmit={add} className="mb-3">
        <Textarea
          rows={2}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Anything worth keeping. First line becomes the title if you write more than one."
        />
        <div className="mt-2 flex justify-end">
          <Button type="submit" disabled={busy || !draft.trim()}>
            <span className="flex items-center gap-1.5">
              <PlusIcon width={15} height={15} />
              {busy ? "Saving…" : "Add note"}
            </span>
          </Button>
        </div>
      </form>

      {notes.length === 0 ? (
        <p className="py-6 text-center text-sm text-mute">Nothing yet.</p>
      ) : (
        <div className="grid gap-2 sm:grid-cols-2">
          {notes.map((note) => (
            <Card key={note.uuid} className="group p-4">
              <div className="flex items-start gap-2">
                <div className="min-w-0 flex-1">
                  {note.title && <p className="font-medium text-paper">{note.title}</p>}
                  <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-soft">{note.body}</p>
                </div>
                <div className="flex shrink-0 gap-1 opacity-0 transition group-hover:opacity-100 focus-within:opacity-100">
                  <button
                    onClick={() => togglePin(note)}
                    aria-label={note.is_pinned ? "Unpin note" : "Pin note"}
                    className={`rounded p-1 transition hover:text-paper ${
                      note.is_pinned ? "text-accent" : "text-mute"
                    }`}
                  >
                    <PinIcon width={15} height={15} />
                  </button>
                  <button
                    onClick={() => remove(note)}
                    aria-label="Delete note"
                    className="rounded p-1 text-mute transition hover:text-bad"
                  >
                    <TrashIcon width={15} height={15} />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
