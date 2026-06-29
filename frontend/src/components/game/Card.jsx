// File prefixes come from the SEASONS associated with Hungarian card suits:
// t = tavasz/spring → Piros (Hearts), s = nyár/summer → Tök (Bells),
// a = ősz/autumn → Zöld (Leaves), w = tél/winter → Makk (Acorns)
const SUIT_TO_PREFIX = { P: 't', T: 's', Z: 'a', M: 'w' };
const VALUE_TO_FILE  = { A: 'asz', K: 'king', Q: 'up', J: 'down', '10': 'x', '9': 'ix', '8': 'viii', '7': 'vii' };

export default function Card({ suit, value, onClick, selected = false }) {
  const src = `/cards/${SUIT_TO_PREFIX[suit]}_${VALUE_TO_FILE[value]}.jpg`;

  return (
    <div
      className={`card${selected ? ' card--selected' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
    >
      <img src={src} alt={`${value} ${suit}`} className="card__img" draggable={false} />
    </div>
  );
}
