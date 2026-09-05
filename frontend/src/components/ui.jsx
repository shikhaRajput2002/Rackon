const OUTCOME_STYLES = {
  RIGHT: "bg-good/15 text-good border-good/30",
  WRONG: "bg-bad/15 text-bad border-bad/30",
  MIXED: "bg-partial/15 text-partial border-partial/30",
  DRAFT: "bg-line text-soft border-line",
  LOCKED: "bg-accent/10 text-accent border-accent/30",
  REVIEWED: "bg-raised text-mute border-line",
};

export function Badge({ children, tone = "DRAFT" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium uppercase tracking-wider ${
        OUTCOME_STYLES[tone] || OUTCOME_STYLES.DRAFT
      }`}
    >
      {children}
    </span>
  );
}

export function Card({ children, className = "" }) {
  return <div className={`rounded-xl border border-line bg-surface ${className}`}>{children}</div>;
}

export function Button({ children, variant = "primary", className = "", ...props }) {
  const variants = {
    primary: "bg-accent text-ink hover:bg-accent/90 disabled:bg-accent/40",
    ghost: "border border-line text-soft hover:border-mute hover:text-paper",
    danger: "border border-bad/40 text-bad hover:bg-bad/10",
  };
  return (
    <button
      className={`rounded-lg px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function Field({ label, hint, children }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-mute">{label}</span>
      {children}
      {hint && <span className="mt-1.5 block text-xs text-mute">{hint}</span>}
    </label>
  );
}

const inputBase =
  "w-full rounded-lg border border-line bg-raised px-3 py-2.5 text-sm text-paper placeholder:text-mute/60 outline-none focus:border-accent/60";

export const Input = (props) => <input className={inputBase} {...props} />;
export const Textarea = (props) => <textarea className={`${inputBase} resize-y`} {...props} />;
export const Select = ({ children, ...props }) => (
  <select className={inputBase} {...props}>
    {children}
  </select>
);

export function StatCard({ label, value, suffix, caption, tone = "paper" }) {
  const tones = { paper: "text-paper", good: "text-good", bad: "text-bad", accent: "text-accent" };
  return (
    <Card className="p-4">
      <p className="text-[11px] font-medium uppercase tracking-wider text-mute">{label}</p>
      <p className={`mt-1.5 text-2xl font-semibold tabular-nums ${tones[tone]}`}>
        {value}
        {suffix && <span className="text-base text-mute">{suffix}</span>}
      </p>
      {caption && <p className="mt-1 text-xs leading-snug text-mute">{caption}</p>}
    </Card>
  );
}

export function ConfidenceSlider({ value, onChange, disabled }) {
  return (
    <div>
      <div className="mb-3 flex items-baseline gap-2">
        <span className="text-4xl font-semibold tabular-nums text-accent">{value}</span>
        <span className="text-lg text-mute">%</span>
        <span className="ml-auto text-xs text-mute">{describeConfidence(value)}</span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        step="1"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full"
      />
      <div className="mt-1.5 flex justify-between text-[11px] text-mute">
        <span>No idea</span>
        <span>Coin flip</span>
        <span>Certain</span>
      </div>
    </div>
  );
}

function describeConfidence(value) {
  if (value >= 90) return "Almost certain";
  if (value >= 75) return "Confident";
  if (value >= 60) return "Leaning yes";
  if (value >= 45) return "Genuinely unsure";
  if (value >= 25) return "Doubtful";
  return "Probably not";
}

export function Empty({ title, children }) {
  return (
    <Card className="p-10 text-center">
      <p className="serif text-lg text-soft">{title}</p>
      {children && <p className="mx-auto mt-2 max-w-md text-sm text-mute">{children}</p>}
    </Card>
  );
}

export function Loading() {
  return <p className="py-16 text-center text-sm text-mute">Loading…</p>;
}
