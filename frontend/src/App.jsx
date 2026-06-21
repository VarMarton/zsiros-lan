import { useState } from "react";
import LobbyPage from "./pages/LobbyPage";
import RoomPage from "./pages/RoomPage";
import GamePage from "./pages/GamePage";

// Simple client-side routing via state — no router library needed yet.
// Screens: "lobby" | "room" | "game"
export default function App() {
  const [screen, setScreen] = useState("lobby");

  if (screen === "room") return <RoomPage onNavigate={setScreen} />;
  if (screen === "game") return <GamePage onNavigate={setScreen} />;
  return <LobbyPage onNavigate={setScreen} />;
}
