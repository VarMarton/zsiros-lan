import Card from './Card.jsx';

export default function Table({ cards, emptyText }) {
  return (
    <div className="table-area">
      <div className="table-surface">
        {cards.length === 0 ? (
          <span className="table-empty-text">{emptyText}</span>
        ) : (
          cards.map((card, i) => (
            <Card key={i} suit={card.suit} value={card.value} />
          ))
        )}
      </div>
    </div>
  );
}
