import { useState } from 'react';
import { translations } from './i18n.js';
import LanguageSwitcher from './components/LanguageSwitcher.jsx';
import LobbyPage from './pages/LobbyPage.jsx';
import CreateRoomPage from './pages/CreateRoomPage.jsx';
import JoinPage from './pages/JoinPage.jsx';
import GamePage from './pages/GamePage.jsx';
import ResultPage from './pages/ResultPage.jsx';

// Dev shortcut: ?screen=game in the URL jumps straight to a screen.
const INITIAL_SCREEN = new URLSearchParams(window.location.search).get('screen') ?? 'lobby';

const DEV_MOCK_DATA = {
  join:   { room: { id: 1, name: 'Barátok szobája', host: 'Zsuzsi', mode: 'classic' } },
  game:   { yourName: 'Béla', roomName: 'Barátok szobája', mode: 'classic' },
  result: { winnerName: 'Zsuzsi', roomName: 'Barátok szobája' },
};

export default function App() {
  const [screen, setScreen]   = useState(INITIAL_SCREEN);
  const [navData, setNavData] = useState(DEV_MOCK_DATA[INITIAL_SCREEN] ?? {});
  const [lang, setLang]       = useState('hu');

  const t = translations[lang];

  function navigate(nextScreen, data = {}) {
    setNavData(data);
    setScreen(nextScreen);
  }

  return (
    <>
      <LanguageSwitcher lang={lang} onChange={setLang} />
      {screen === 'create' && <CreateRoomPage t={t} onNavigate={navigate} />}
      {screen === 'join'   && <JoinPage       t={t} data={navData} onNavigate={navigate} />}
      {screen === 'game'   && <GamePage       t={t.game} onNavigate={navigate} />}
      {screen === 'result' && <ResultPage     t={t} data={navData} onNavigate={navigate} />}
      {!['create', 'join', 'game', 'result'].includes(screen) && (
        <LobbyPage t={t} onNavigate={navigate} />
      )}
    </>
  );
}
