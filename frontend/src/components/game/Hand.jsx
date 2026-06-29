import { useState } from 'react';
import Card from './Card.jsx';

export default function Hand({ cards, playerName, points, canYield, onYield, onPlayCard, t }) {
  const [selectedIndex, setSelectedIndex] = useState(null);

  function handleCardClick(index) {
    if (selectedIndex === index) {
      onPlayCard?.(cards[index]);
      setSelectedIndex(null);
    } else {
      setSelectedIndex(index);
    }
  }

  return (
    <div className="bottom-area">
      <div className="hand-row">
        {cards.map((card, i) => (
          <Card
            key={i}
            suit={card.suit}
            value={card.value}
            selected={selectedIndex === i}
            onClick={() => handleCardClick(i)}
          />
        ))}
      </div>
      <div className="player-info-row">
        <div className="player-name-pts">
          <span className="player-name">{playerName}</span>
          <span className="player-pts">{points} pt</span>
        </div>
        <button
          className={`yield-btn${canYield ? ' yield-btn--visible' : ''}`}
          onClick={onYield}
          aria-hidden={!canYield}
          tabIndex={canYield ? 0 : -1}
        >
          {t.yield}
        </button>
      </div>
    </div>
  );
}
