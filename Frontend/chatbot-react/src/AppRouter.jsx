
import { Routes, Route } from "react-router-dom";
import Inicio from "./pages/Inicio";
import Chat from "./pages/Chat";
import Politicas from "./pages/Politicas";

function AppRouter() {
  

  return (
    <Routes>
      
      <Route path="/" element={<Inicio />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/politicas" element={<Politicas />} />
    </Routes>
  );
}

export default AppRouter;
