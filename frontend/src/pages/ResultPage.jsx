export default function ResultPage({ t, data, onNavigate }) {
  const tr = t.result;
  const { winnerName, roomName } = data;

  return (
    <div className="result-page">
      <div className="result-trophy">🏆</div>
      <div>
        <div className="result-winner-name">{winnerName}</div>
        <div className="result-winner-label">{tr.winner}</div>
      </div>
      <p className="result-room">
        {tr.room}: <span>{roomName}</span>
      </p>
      <div className="result-actions">
        <button className="btn btn--primary" onClick={() => onNavigate('game')}>
          {tr.playAgain}
        </button>
        <button className="btn btn--secondary" onClick={() => onNavigate('lobby')}>
          {tr.backToLobby}
        </button>
      </div>
    </div>
  );
}
