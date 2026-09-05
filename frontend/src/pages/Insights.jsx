import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import { Card, Empty, Loading, StatCard } from "../components/ui";

// Validated for dark-surface contrast and colour-vision separation.
const CLAIMED = "#b8842c";
const ACTUAL = "#5b8dd9";

export default function Insights() {
  const [record, setRecord] = useState(null);

  useEffect(() => {
    api("/insights/track-record/").then(setRecord);
  }, []);

  if (!record) return <Loading />;

  if (!record.has_enough_data) {
    return (
      <Empty title={`${record.reviewed_count} of ${record.minimum_reviews} decisions scored.`}>
        Calibration needs a handful of finished decisions before it says anything true. Patterns before then are
        noise, not signal.
      </Empty>
    );
  }

  const buckets = record.buckets.filter((bucket) => bucket.count > 0);
  const gap = record.calibration_gap;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="serif text-2xl text-paper">Your track record</h1>
        <p className="mt-1.5 text-sm text-mute">
          Based on {record.reviewed_count} decisions you scored after the fact.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <StatCard
          label="You were right"
          value={record.accuracy_percent}
          suffix="%"
          caption="Partly-right outcomes count as half"
        />
        <StatCard
          label="Confidence gap"
          value={gap > 0 ? `+${gap}` : gap}
          caption={
            gap > 5
              ? "You claim more certainty than you earn"
              : gap < -5
                ? "You are right more often than you claim"
                : "Your confidence means what it says"
          }
          tone={gap > 5 ? "bad" : gap < -5 ? "accent" : "good"}
        />
        <StatCard
          label="Brier score"
          value={record.brier_score}
          caption="0 is perfect · 0.25 is a coin flip"
        />
      </div>

      <Card className="p-6">
        <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="font-medium text-paper">Confidence against reality</h2>
          <Legend />
        </div>
        <p className="mb-6 text-sm text-mute">
          If you were perfectly calibrated the two bars would match in every group.
        </p>

        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={buckets} margin={{ top: 8, right: 8, bottom: 8, left: -18 }} barGap={2}>
            <CartesianGrid stroke="#2a2a2e" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: "#8a8a93", fontSize: 12 }}
              axisLine={{ stroke: "#2a2a2e" }}
              tickLine={false}
            />
            <YAxis
              domain={[0, 100]}
              unit="%"
              tick={{ fill: "#8a8a93", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip cursor={{ fill: "#ffffff08" }} content={<BucketTooltip />} />
            <Bar
              dataKey="claimed"
              name="You said"
              fill={CLAIMED}
              radius={[4, 4, 0, 0]}
              maxBarSize={38}
              minPointSize={2}
              isAnimationActive={false}
            />
            <Bar
              dataKey="actual"
              name="You were"
              fill={ACTUAL}
              radius={[4, 4, 0, 0]}
              maxBarSize={38}
              minPointSize={2}
              isAnimationActive={false}
            />
          </BarChart>
        </ResponsiveContainer>

        <p className="mt-4 border-t border-line pt-4 text-sm text-soft">
          {gap > 5
            ? `When you say you are sure, you are about ${Math.round(gap)} points less sure than that.`
            : gap < -5
              ? `You undersell yourself by about ${Math.round(Math.abs(gap))} points — you are probably passing on calls you should make.`
              : "Your stated confidence tracks your actual hit rate closely. That is rare."}
        </p>
      </Card>

      <Card className="p-6">
        <h2 className="font-medium text-paper">Where you go wrong</h2>
        <p className="mb-6 mt-1 text-sm text-mute">
          Accuracy by kind of decision. Your weakest is {record.weakest_category?.toLowerCase()}.
        </p>
        <ResponsiveContainer width="100%" height={record.by_category.length * 42 + 20}>
          <BarChart data={record.by_category} layout="vertical" margin={{ top: 0, right: 44, bottom: 0, left: 12 }}>
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis
              type="category"
              dataKey="category"
              width={104}
              tick={{ fill: "#b8b8c0", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip cursor={{ fill: "#ffffff08" }} content={<CategoryTooltip />} />
            <Bar
              dataKey="accuracy"
              radius={[0, 4, 4, 0]}
              maxBarSize={18}
              minPointSize={2}
              isAnimationActive={false}
              label={<AccuracyLabel />}
              fill={ACTUAL}
            />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <ChallengeEffect effect={record.challenge_effect} />
    </div>
  );
}

function Legend() {
  return (
    <div className="flex items-center gap-4 text-xs text-mute">
      <span className="flex items-center gap-1.5">
        <span className="h-2.5 w-2.5 rounded-sm" style={{ background: CLAIMED }} />
        You said
      </span>
      <span className="flex items-center gap-1.5">
        <span className="h-2.5 w-2.5 rounded-sm" style={{ background: ACTUAL }} />
        You were
      </span>
    </div>
  );
}

function BucketTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-lg border border-line bg-raised px-3 py-2 text-xs shadow-lg">
      <p className="mb-1.5 font-medium text-paper">
        {label} confidence · {row.count} decision{row.count > 1 ? "s" : ""}
      </p>
      <p style={{ color: CLAIMED }}>Claimed {row.claimed}% sure</p>
      <p style={{ color: ACTUAL }}>Actually right {row.actual}% of the time</p>
    </div>
  );
}

function CategoryTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-lg border border-line bg-raised px-3 py-2 text-xs shadow-lg">
      <p className="font-medium text-paper">{row.category}</p>
      <p className="mt-1 text-soft">
        Right {row.accuracy}% across {row.count} decision{row.count > 1 ? "s" : ""}
      </p>
      <p className="text-mute">Average confidence {row.average_confidence}%</p>
    </div>
  );
}

function AccuracyLabel({ x, y, width, height, value }) {
  return (
    <text x={x + width + 8} y={y + height / 2} fill="#8a8a93" fontSize={12} dominantBaseline="middle">
      {value}%
    </text>
  );
}

function ChallengeEffect({ effect }) {
  if (!effect.moved_count) {
    return (
      <Card className="p-6">
        <h2 className="font-medium text-paper">Does arguing change your mind?</h2>
        <p className="mt-1.5 text-sm text-mute">
          No scored decision has had its confidence revised yet. Challenge a few and this will fill in.
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h2 className="font-medium text-paper">Does arguing change your mind?</h2>
      <p className="mt-1.5 text-sm text-mute">
        On {effect.moved_count} scored decision{effect.moved_count > 1 ? "s" : ""} the challenge moved your
        confidence by {effect.average_shift} points on average.
      </p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-line bg-raised p-4">
          <p className="text-[11px] font-medium uppercase tracking-wider text-mute">When it moved you</p>
          <p className="mt-1 text-xl font-semibold tabular-nums text-paper">
            {effect.gap_when_moved > 0 ? "+" : ""}
            {effect.gap_when_moved}
            <span className="ml-1.5 text-xs font-normal text-mute">point gap</span>
          </p>
        </div>
        <div className="rounded-lg border border-line bg-raised p-4">
          <p className="text-[11px] font-medium uppercase tracking-wider text-mute">When it did not</p>
          <p className="mt-1 text-xl font-semibold tabular-nums text-paper">
            {effect.gap_when_unmoved === null ? (
              <span className="text-base font-normal text-mute">Not enough data</span>
            ) : (
              <>
                {effect.gap_when_unmoved > 0 ? "+" : ""}
                {effect.gap_when_unmoved}
                <span className="ml-1.5 text-xs font-normal text-mute">point gap</span>
              </>
            )}
          </p>
        </div>
      </div>
      <p className="mt-4 text-sm text-soft">
        A smaller gap on the left means the challenge is doing real work — it is making you better calibrated,
        not just quieter.
      </p>
    </Card>
  );
}
