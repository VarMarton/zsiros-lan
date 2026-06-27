// Mock room list — replaced later by WebSocket-driven state.
const MOCK_ROOMS = [
  { id: 1, name: 'Barátok szobája', host: 'Zsuzsi', mode: 'classic', open: true },
  { id: 2, name: 'Profi meccs', host: 'Béla', mode: 'classic', open: true },
  { id: 3, name: 'Már folyamatban', host: 'Kata', mode: 'classic', open: false },
];

export default function LobbyPage({ t, onNavigate }) {
  const tl = t.lobby;
  const openRooms   = MOCK_ROOMS.filter(r => r.open);
  const closedRooms = MOCK_ROOMS.filter(r => !r.open);

  return (
    <div className="page">
      <div className="lobby-hero">
        <h1 className="lobby-title">
          Zsíros <span>LAN</span>
        </h1>
        <button className="btn btn--primary" style={{ width: '100%', maxWidth: '320px' }} onClick={() => onNavigate('create')}>
          {tl.newRoom}
        </button>
      </div>

      <div className="page-content">
        <div className="section-label">{tl.openRooms}</div>
        <div className="room-list">
          {openRooms.length === 0 ? (
            <p className="empty-state">{tl.noOpenRooms}</p>
          ) : (
            openRooms.map(room => (
              <div key={room.id} className="room-item">
                <div className="room-info">
                  <div className="room-name">{room.name}</div>
                  <div className="room-host">{tl.host}: {room.host}</div>
                </div>
                <button
                  className="room-join-btn"
                  onClick={() => onNavigate('join', { room })}
                >
                  {tl.join}
                </button>
              </div>
            ))
          )}
        </div>

        <div className="section-label">{tl.closedRooms}</div>
        <div className="room-list">
          {closedRooms.length === 0 ? (
            <p className="empty-state">{tl.noClosedRooms}</p>
          ) : (
            closedRooms.map(room => (
              <div key={room.id} className="room-item room-item--closed">
                <div className="room-info">
                  <div className="room-name">{room.name}</div>
                  <div className="room-host">{tl.host}: {room.host}</div>
                </div>
                <span className="room-lock">🔒</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
