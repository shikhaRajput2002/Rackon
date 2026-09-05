import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { AdvisorIcon, ChartIcon, HomeIcon, LedgerIcon, UserIcon } from "./icons";

const NAV = [
  { to: "/", label: "Home", Icon: HomeIcon, end: true },
  { to: "/decisions", label: "Decisions", Icon: LedgerIcon },
  { to: "/insights", label: "Insights", Icon: ChartIcon },
  { to: "/ask", label: "Ask", Icon: AdvisorIcon },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    api("/decisions/notifications/?unread=true").then(setNotifications).catch(() => {});
  }, [location.pathname]);

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-line bg-ink/85 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center gap-5 px-6 py-3.5">
          <Link to="/" className="serif text-lg tracking-tight text-paper">
            Reckon
          </Link>
          <nav className="flex gap-0.5">
            {NAV.map(({ to, label, Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm transition ${
                    isActive ? "bg-raised text-paper" : "text-mute hover:text-soft"
                  }`
                }
              >
                <Icon width={16} height={16} />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3">
            <Link
              to="/new"
              className="rounded-lg bg-accent px-3 py-1.5 text-sm font-medium text-ink transition hover:bg-accent/90"
            >
              Log a decision
            </Link>
            <NavLink
              to="/profile"
              title={user?.email}
              aria-label="Your details"
              className={({ isActive }) =>
                `rounded-lg p-1.5 transition ${isActive ? "bg-raised text-paper" : "text-mute hover:text-soft"}`
              }
            >
              <UserIcon width={18} height={18} />
            </NavLink>
            <button onClick={logout} className="text-sm text-mute transition hover:text-soft">
              Sign out
            </button>
          </div>
        </div>
      </header>

      {notifications.length > 0 && location.pathname === "/decisions" && (
        <div className="border-b border-accent/20 bg-accent/[0.07]">
          <div className="mx-auto max-w-5xl px-6 py-3">
            <p className="text-sm text-accent">
              {notifications.length} decision{notifications.length > 1 ? "s are" : " is"} ready to be scored.
            </p>
            <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1">
              {notifications.map((notification) => (
                <Link
                  key={notification.uuid}
                  to={`/decisions/${notification.decision_uuid}`}
                  className="text-sm text-soft underline decoration-line underline-offset-4 hover:text-paper"
                >
                  {notification.title.replace("Time to score: ", "")}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      <main className="mx-auto max-w-5xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
