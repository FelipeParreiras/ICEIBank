import { useAuth } from "./hooks/useAuth";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  const { autenticado } = useAuth();
  return autenticado ? <DashboardPage /> : <LoginPage />;
}
