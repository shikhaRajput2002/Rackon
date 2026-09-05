import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";
import { AdvisorIcon, AlertIcon, CalculatorIcon, LedgerIcon, ScaleIcon, UserIcon } from "../components/icons";
import { Button, Card, Input } from "../components/ui";

const SUGGESTIONS = [
  "Should I get the Aprilia RS 457 for 4.2 lakh?",
  "Should I learn swimming?",
  "Am I overconfident?",
];

const TOPIC_LABELS = {
  MONEY: "Affordability",
  TRACK_RECORD: "Your record",
  GENERAL: "Worth thinking about",
};

export default function Ask() {
  const navigate = useNavigate();
  // Coming back from the profile form, the question we could not answer is
  // handed back so it is sitting in the box, ready to send.
  const returned = useLocation().state?.pendingQuestion;

  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState(returned || "");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState(null);
  const [blockedQuestion, setBlockedQuestion] = useState(null);
  const [busy, setBusy] = useState(false);
  const endRef = useRef(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    api("/advisor/").then(setMessages);
  }, []);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  async function ask(text) {
    const asked = (text ?? question).trim();
    if (!asked || busy) return;

    setQuestion("");
    setError(null);
    setBlockedQuestion(null);
    setBusy(true);
    setMessages((current) => [...current, { uuid: `local-${Date.now()}`, role: "user", content: asked }]);

    try {
      const answer = await api("/advisor/", {
        method: "POST",
        body: { question: asked, ...(amount ? { amount } : {}) },
      });
      setMessages((current) => [...current, answer]);
      setAmount("");
    } catch (caught) {
      setError(caught);
      setBlockedQuestion(asked);
      setMessages((current) => current.filter((message) => !String(message.uuid).startsWith("local-")));
    }
    setBusy(false);
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <header className="flex items-start gap-3">
        <span className="mt-0.5 shrink-0 rounded-lg border border-accent/30 bg-accent/10 p-2 text-accent">
          <AdvisorIcon />
        </span>
        <div>
          <h1 className="serif text-2xl text-paper">Ask before you commit</h1>
          <p className="mt-1.5 text-sm leading-relaxed text-mute">
            Money questions get real arithmetic from your own figures. Everything else gets the questions
            worth sitting with. Neither will tell you what to do.
          </p>
        </div>
      </header>

      {messages.length === 0 && !busy && !error && (
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => ask(suggestion)}
              className="rounded-full border border-line px-3.5 py-1.5 text-sm text-soft transition hover:border-mute hover:text-paper"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      <div className="space-y-4">
        {messages.map((message) =>
          message.role === "user" ? (
            <div key={message.uuid} className="flex justify-end">
              <p className="max-w-[85%] rounded-2xl rounded-br-sm bg-raised px-4 py-2.5 text-sm leading-relaxed text-paper">
                {message.content}
              </p>
            </div>
          ) : (
            <Answer
              key={message.uuid}
              message={message}
              onLog={(suggestion) => navigate("/new", { state: { prefill: suggestion } })}
            />
          ),
        )}

        {busy && (
          <p className="flex items-center gap-2 text-sm text-mute">
            <AdvisorIcon width={16} height={16} className="text-accent" />
            Working through your numbers…
          </p>
        )}

        {error && (
          <Card className="border-accent/30 p-5">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 shrink-0 text-accent">
                <AlertIcon width={18} height={18} />
              </span>
              <div>
                <p className="text-sm leading-relaxed text-soft">{error.message}</p>
                {error.code === "PROFILE_REQUIRED_FOR_MONEY" && (
                  <Button
                    className="mt-3"
                    onClick={() =>
                      navigate("/profile", {
                        state: { returnTo: "/ask", pendingQuestion: blockedQuestion },
                      })
                    }
                  >
                    <span className="flex items-center gap-1.5">
                      <UserIcon width={15} height={15} />
                      Add your details
                    </span>
                  </Button>
                )}
              </div>
            </div>
          </Card>
        )}
        <div ref={endRef} />
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          ask();
        }}
        className="sticky bottom-6 space-y-2 rounded-xl border border-line bg-surface/95 p-3 backdrop-blur"
      >
        <div className="flex gap-2">
          <Input
            autoFocus={Boolean(returned)}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Should I buy…?   Should I start…?"
          />
          <Button type="submit" disabled={busy || !question.trim()}>
            Ask
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-mute">If the price is not in your question:</span>
          <input
            type="number"
            min="0"
            step="1000"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            placeholder="amount"
            aria-label="Amount involved"
            className="w-32 rounded-lg border border-line bg-raised px-2.5 py-1.5 text-xs tabular-nums text-paper placeholder:text-mute/60 outline-none focus:border-accent/60"
          />
        </div>
      </form>
    </div>
  );
}

function Answer({ message, onLog }) {
  const suggestion = message.suggested_decision;
  const hasSuggestion = suggestion && Object.keys(suggestion).length > 0;

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center gap-2 border-b border-line bg-raised px-5 py-2.5">
        <AdvisorIcon width={15} height={15} className="text-accent" />
        <span className="text-[11px] uppercase tracking-wider text-mute">
          {TOPIC_LABELS[message.topic] || TOPIC_LABELS.GENERAL}
        </span>
        <span className="ml-auto text-[11px] uppercase tracking-wider text-mute">via {message.provider}</span>
      </div>

      <div className="divide-y divide-line">
        <p className="whitespace-pre-wrap p-5 text-[15px] leading-[1.7] text-soft">{message.content}</p>

        {message.numbers?.length > 0 && (
          <Block Icon={CalculatorIcon} title="The arithmetic">
            <dl className="space-y-3">
              {message.numbers.map((row) => (
                <div key={row.label} className="grid grid-cols-[1fr_auto] items-baseline gap-x-4 gap-y-0.5">
                  <dt className="text-sm text-soft">{row.label}</dt>
                  <dd className="text-right text-sm font-semibold tabular-nums text-paper">{row.value}</dd>
                  {row.note && <p className="col-span-2 -mt-0.5 text-xs leading-snug text-mute">{row.note}</p>}
                </div>
              ))}
            </dl>
          </Block>
        )}

        {message.considerations?.length > 0 && (
          <Block Icon={ScaleIcon} title="What this actually costs you">
            <Bullets items={message.considerations} />
          </Block>
        )}

        {message.watch_outs?.length > 0 && (
          <Block Icon={AlertIcon} title="Not in the numbers">
            <Bullets items={message.watch_outs} />
          </Block>
        )}

        {hasSuggestion && (
          <div className="bg-accent/[0.06] p-5">
            <p className="text-sm leading-relaxed text-soft">
              Whichever way you go — write it down now, while you still do not know the answer.
            </p>
            <Button onClick={() => onLog(suggestion)} className="mt-3">
              <span className="flex items-center gap-1.5">
                <LedgerIcon width={15} height={15} />
                Log this as a decision
              </span>
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}

function Block({ Icon, title, children }) {
  return (
    <section className="p-5">
      <div className="mb-3 flex items-center gap-2">
        <Icon width={15} height={15} className="text-accent" />
        <h3 className="text-[11px] font-medium uppercase tracking-wider text-mute">{title}</h3>
      </div>
      {children}
    </section>
  );
}

function Bullets({ items }) {
  return (
    <ul className="space-y-2.5">
      {items.map((item, index) => (
        <li key={index} className="flex gap-3 text-[15px] leading-[1.65] text-soft">
          <span aria-hidden="true" className="mt-[9px] h-1 w-1 shrink-0 rounded-full bg-accent" />
          {item}
        </li>
      ))}
    </ul>
  );
}
