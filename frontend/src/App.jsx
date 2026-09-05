import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Layout from "./components/Layout";
import { Loading } from "./components/ui";
import Ask from "./pages/Ask";
import Dashboard from "./pages/Dashboard";
import DecisionDetail from "./pages/DecisionDetail";
import Home from "./pages/Home";
import Insights from "./pages/Insights";
import Login from "./pages/Login";
import NewDecision from "./pages/NewDecision";
import Profile from "./pages/Profile";

function Routing() {
  const { user, loading } = useAuth();

  if (loading) return <Loading />;
  if (!user) return <Login />;

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/decisions" element={<Dashboard />} />
        <Route path="/decisions/:uuid" element={<DecisionDetail />} />
        <Route path="/new" element={<NewDecision />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/ask" element={<Ask />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routing />
      </AuthProvider>
    </BrowserRouter>
  );
}
