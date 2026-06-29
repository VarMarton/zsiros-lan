function ZsirBadge({ type }) {
  return (
    <div className={`zsir-badge zsir-badge--${type}`}>
      {type === 'ace' ? 'A' : '10'}
    </div>
  );
}

function ZsirPile({ label, aces, tens }) {
  const totalCards = aces + tens;

  return (
    <div className="zsir-pile">
      <span className="zsir-pile__label">{label}</span>
      <div className="zsir-pile__cards">
        {Array.from({ length: aces }).map((_, i) => (
          <ZsirBadge key={`a${i}`} type="ace" />
        ))}
        {Array.from({ length: tens }).map((_, i) => (
          <ZsirBadge key={`t${i}`} type="ten" />
        ))}
        {totalCards === 0 && (
          <span className="zsir-pile__empty">–</span>
        )}
      </div>
    </div>
  );
}

export default function ZsirCollector({ myZsir, oppZsir, t }) {
  return (
    <div className="zsir-collector">
      <ZsirPile label={t.me} aces={myZsir.aces} tens={myZsir.tens} />
      <ZsirPile label={t.opp} aces={oppZsir.aces} tens={oppZsir.tens} />
    </div>
  );
}
