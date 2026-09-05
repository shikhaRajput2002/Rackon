import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";
import { Button, Card, ConfidenceSlider, Field, Input, Select, Textarea } from "../components/ui";

const CATEGORIES = ["CAREER", "MONEY", "PRODUCT", "HEALTH", "RELATIONSHIP", "LEARNING", "OTHER"];

function defaultReviewDate() {
  const date = new Date();
  date.setDate(date.getDate() + 30);
  return date.toISOString().slice(0, 10);
}

export default function NewDecision() {
  const navigate = useNavigate();
  // The advisor hands a decision over through router state, so "log this" lands
  // on a form that is already mostly filled in.
  const prefill = useLocation().state?.prefill;

  const [form, setForm] = useState({
    title: prefill?.title ?? "",
    category: prefill?.category ?? "CAREER",
    context: "",
    chosen_option: prefill?.chosen_option ?? "",
    expected_outcome: prefill?.expected_outcome ?? "",
    review_date: defaultReviewDate(),
  });
  const [options, setOptions] = useState(
    prefill ? [prefill.chosen_option ?? "", "Do nothing for now"] : ["", ""],
  );
  const [confidence, setConfidence] = useState(prefill?.initial_confidence ?? 70);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const update = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  function updateOption(index, value) {
    const next = [...options];
    next[index] = value;
    setOptions(next);
  }

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const decision = await api("/decisions/", {
        method: "POST",
        body: {
          ...form,
          options_considered: options.map((option) => option.trim()).filter(Boolean),
          initial_confidence: confidence,
        },
      });
      navigate(`/decisions/${decision.uuid}`);
    } catch (caught) {
      setError(caught.message);
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="serif text-2xl text-paper">Log a decision</h1>
        <p className="mt-1.5 text-sm text-mute">
          {prefill
            ? "Brought over from the advisor. Check it reads like your own words, then say why."
            : "Write this the way you would explain it to someone who will hold you to it later."}
        </p>
      </div>

      <Card className="space-y-5 p-6">
        <Field label="The decision">
          <Input
            required
            value={form.title}
            onChange={update("title")}
            placeholder="Take the offer at the smaller company"
          />
        </Field>

        <Field label="Category">
          <Select value={form.category} onChange={update("category")}>
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category.charAt(0) + category.slice(1).toLowerCase()}
              </option>
            ))}
          </Select>
        </Field>

        <Field label="Why you are deciding this" hint="The reasoning you would be embarrassed to have forgotten.">
          <Textarea
            required
            rows={4}
            value={form.context}
            onChange={update("context")}
            placeholder="What is pushing this decision now, and what is actually at stake."
          />
        </Field>

        <Field label="Options you weighed">
          <div className="space-y-2">
            {options.map((option, index) => (
              <Input
                key={index}
                value={option}
                onChange={(event) => updateOption(index, event.target.value)}
                placeholder={index === 0 ? "Take the offer" : "Stay where I am"}
              />
            ))}
          </div>
          <button
            type="button"
            onClick={() => setOptions([...options, ""])}
            className="mt-2 text-xs text-accent transition hover:text-accent/80"
          >
            + Add another option
          </button>
        </Field>

        <Field label="What you are going with">
          <Input required value={form.chosen_option} onChange={update("chosen_option")} placeholder="Take the offer" />
        </Field>

        <Field label="What you expect to happen" hint="Be specific enough that you could be proven wrong.">
          <Textarea
            required
            rows={3}
            value={form.expected_outcome}
            onChange={update("expected_outcome")}
            placeholder="Within six months I am leading a project end to end and I have not regretted the pay cut."
          />
        </Field>

        <Field label="Come back and score this on" hint="Far enough out that the answer will actually be known.">
          <Input type="date" required value={form.review_date} onChange={update("review_date")} />
        </Field>
      </Card>

      <Card className="p-6">
        <p className="mb-4 text-xs font-medium uppercase tracking-wider text-mute">
          How confident are you that this works out?
        </p>
        <ConfidenceSlider value={confidence} onChange={setConfidence} />
      </Card>

      {error && <p className="text-sm text-bad">{error}</p>}

      <div className="flex gap-3">
        <Button type="submit" disabled={busy}>
          {busy ? "Saving…" : "Save as draft"}
        </Button>
        <Button type="button" variant="ghost" onClick={() => navigate("/")}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
