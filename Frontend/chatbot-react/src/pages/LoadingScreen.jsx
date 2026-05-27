import { useEffect } from "react";
import Loader from "./Loader"; // ajusta la ruta según donde pongas el Loader

function LoadingScreen({ onFinish }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onFinish();
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
      background: "#000",
      gap: "20px"
    }}>
      <Loader />
      <p style={{
        color: "#b000ff",
        fontSize: "16px",
        fontFamily: "Segoe UI, sans-serif",
        textShadow: "0 0 10px #b000ff"
      }}>
        Cargando...
      </p>
    </div>
  );
}

export default LoadingScreen;