export default function TopBar({ myHandCount, oppHandCount, isMyTurn, onMenuOpen, t }) {
  return (
    <div className="top-bar">
      <button className="top-bar__menu-btn" onClick={onMenuOpen} aria-label="Menu">
        ☰
      </button>
      <div className="top-bar__counters">
        <div className={`counter-chip${!isMyTurn ? ' counter-chip--active' : ''}`}>
          <span>{t.opp}:</span>
          <span className="counter-chip__count">{oppHandCount}</span>
        </div>
        <div className={`counter-chip${isMyTurn ? ' counter-chip--active' : ''}`}>
          <span>{t.me}:</span>
          <span className="counter-chip__count">{myHandCount}</span>
        </div>
      </div>
    </div>
  );
}
