import { ToastContainer } from "react-toastify";

import { useAuth } from "./hooks/useAuth";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  const { autenticado } = useAuth();
  return (
    <>
      {autenticado ? <DashboardPage /> : <LoginPage />}
      <ToastContainer
        position="top-right"
        autoClose={4500}
        closeOnClick
        pauseOnHover
        newestOnTop
        limit={4}
      />
    </>
  );
}
