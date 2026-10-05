import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import { AgenciaProvider } from "./context/AgenciaContext";
import { AuthProvider } from "./context/AuthContext";
import "react-toastify/dist/ReactToastify.css";
import "./styles/global.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AgenciaProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </AgenciaProvider>
  </StrictMode>,
);
