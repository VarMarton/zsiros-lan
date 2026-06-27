import { useState } from 'react';
import TopBar from '../components/game/TopBar.jsx';
import ZsirCollector from '../components/game/ZsirCollector.jsx';
import Table from '../components/game/Table.jsx';
import Hand from '../components/game/Hand.jsx';
import MenuDrawer from '../components/game/MenuDrawer.jsx';

// Mock game state — replaced later by WebSocket-driven state.
const MOCK_STATE = {
  myName: 'Zsuzsi',
  myPoints: 12,
  isMyTurn: true,
  myHand: [
    { suit: 'P', value: 'K' },
    { suit: 'M', value: '7' },
    { suit: 'T', value: '10' },
    { suit: 'Z', value: 'A' },
    { suit: 'P', value: '8' },
  ],
  oppHandCount: 4,
  tableCards: [
    { suit: 'M', value: 'Q' },
    { suit: 'P', value: '9' },
  ],
  myZsir:  { aces: 2, tens: 1 },
  oppZsir: { aces: 1, tens: 2 },
  canYield: true,
};

export default function GamePage({ t }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const {
    myName, myPoints, isMyTurn,
    myHand, oppHandCount,
    tableCards,
    myZsir, oppZsir,
    canYield,
  } = MOCK_STATE;

  return (
    <div className="game-screen">
      <div className="game-upper">
        <div className="game-main-col">
          <TopBar
            myHandCount={myHand.length}
            oppHandCount={oppHandCount}
            isMyTurn={isMyTurn}
            onMenuOpen={() => setMenuOpen(true)}
            t={t}
          />
          <Table cards={tableCards} emptyText={t.noCards} />
        </div>
        <ZsirCollector myZsir={myZsir} oppZsir={oppZsir} t={t} />
      </div>

      <Hand
        cards={myHand}
        playerName={myName}
        points={myPoints}
        canYield={canYield}
        onYield={() => console.log('yield')}
        onPlayCard={card => console.log('play', card)}
        t={t}
      />

      <MenuDrawer open={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}
