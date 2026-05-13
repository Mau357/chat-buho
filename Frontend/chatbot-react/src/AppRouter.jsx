
import { Routes, Route } from "react-router-dom";
import Inicio from "./pages/Inicio";
import Chat from "./pages/Chat";
import Politicas from "./pages/Politicas";
import AcercaDe from "./pages/acerca-de";

import Sugerencias from "./pages/sugerencias";

function AppRouter() {
  

  return (
    <Routes>
      
      <Route path="/" element={<Inicio />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/Politicas" element={<Politicas />} />
      <Route path="/acerca-de" element={<AcercaDe />} />
      <Route path="/sugerencias" element={<Sugerencias />} />
    </Routes>
  );
}

export default AppRouter;
