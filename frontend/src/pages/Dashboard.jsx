import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { Badge, Card, Empty, Loading, StatCard } from "../components/ui";

const FILTERS = [
  { value: "", label: "All" },
  { value: "DRAFT", label: "Drafts" },
  { value: "LOCKED", label: "Waiting" },
  { value: "REVIEWED", label: "Scored" },
];

export default function Dashboard() {
  const [decisions, setDecisions] = useState(null);
  const [record, setRecord] = useState(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api(`/decisions/${filter ? `?status=${filter}` : ""}`).then((data) => setDecisions(data.results));
  }, [filter]);

  useEffect(() => {
    api("/insights/track-record/").then(setRecord);
  }, []);

  return (
    <div className="space-y-8">
      {record && (
        <div className="grid gap-3 sm:grid-cols-4">
          <StatCard label="Decisions" value={record.total_decisions} caption={`${record.draft_count} still in draft`} />
          <StatCard
            label="Waiting on reality"
            value={record.locked_count}
            caption="Locked, not yet scored"
            tone="accent"
          />
          <StatCard
            label="You were right"
            value={record.has_enough_data ? record.accuracy_percent : "—"}
            suffix={record.has_enough_data ? "%" : null}
            caption={`Across ${record.reviewed_count} scored decisions`}
          />
          <StatCard
            label="Confidence gap"
            value={record.has_enough_data ? (record.calibration_gap > 0 ? `+${record.calibration_gap}` : record.calibration_gap) : "—"}
            caption={
              !record.has_enough_data
                ? `Needs ${record.minimum_reviews} scored`
                : record.calibration_gap > 5
                  ? "You are overconfident"
                  : record.calibration_gap < -5
                    ? "You are underconfident"
                    : "Well calibrated"
            }
            tone={record.calibration_gap > 5 ? "bad" : "good"}
          />
        </div>
      )}

      <div>
        <div className="mb-4 flex items-center gap-1">
          {FILTERS.map((option) => (
            <button
              key={option.value}
              onClick={() => setFilter(option.value)}
              className={`rounded-lg px-3 py-1.5 text-sm transition ${
                filter === option.value ? "bg-raised text-paper" : "text-mute hover:text-soft"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        {decisions === null ? (
          <Loading />
        ) : decisions.length === 0 ? (
          <Empty title="Nothing here yet.">
            Log a decision you are about to make, before you know how it turns out. That is the only way this
            works.
          </Empty>
        ) : (
          <div className="space-y-2">
            {decisions.map((decision) => (
              <DecisionRow key={decision.uuid} decision={decision} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function DecisionRow({ decision }) {
  const outcome = decision.review?.outcome;
  return (
    <Link to={`/decisions/${decision.uuid}`} className="block">
      <Card className="p-4 transition hover:border-mute/50">
        <div className="flex items-start gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <p className="truncate font-medium text-paper">{decision.title}</p>
              <Badge tone={outcome || decision.status}>{outcome || decision.status}</Badge>
              <span className="text-[11px] uppercase tracking-wider text-mute">{decision.category}</span>
            </div>
            <p className="mt-1.5 line-clamp-1 text-sm text-mute">{decision.chosen_option}</p>
          </div>
          <div className="shrink-0 text-right">
            <p className="text-lg font-semibold tabular-nums text-accent">{decision.scored_confidence}%</p>
            {decision.confidence_shift ? (
              <p className="text-[11px] text-mute">
                {decision.confidence_shift > 0 ? "+" : ""}
                {decision.confidence_shift} after challenge
              </p>
            ) : (
              <p className="text-[11px] text-mute">
                {decision.status === "REVIEWED" ? "final" : `review ${decision.review_date}`}
              </p>
            )}
          </div>
        </div>
      </Card>
    </Link>
  );
}
