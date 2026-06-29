export default function MenuDrawer({ open, onClose }) {
  if (!open) return null;

  return (
    <div className="menu-drawer-backdrop" onClick={onClose}>
      <div className="menu-drawer" onClick={e => e.stopPropagation()}>
        <div className="menu-drawer__title">Zsíros LAN</div>
        <div className="menu-drawer__item">Szabályok</div>
        <div className="menu-drawer__item">Újraindítás</div>
        <div className="menu-drawer__item">Kilépés</div>
        <button className="menu-drawer__close-btn" onClick={onClose}>
          Bezár ✕
        </button>
      </div>
    </div>
  );
}
