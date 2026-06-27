import { useState } from 'react';

export default function JoinPage({ t, data, onNavigate }) {
  const tj = t.join;
  const { room } = data;
  const [yourName, setYourName] = useState('');

  function handleSubmit() {
    if (!yourName.trim()) return;
    onNavigate('game', { yourName: yourName.trim(), roomName: room.name, mode: room.mode });
  }

  return (
    <div className="page">
      <div className="page-header">
        <button className="page-back-btn" onClick={() => onNavigate('lobby')}>
          {tj.back}
        </button>
        <h1 className="page-title">{tj.title}</h1>
      </div>

      <div className="page-content">
        <div className="join-info-block">
          <div className="join-info-row">
            <span className="join-info-key">{tj.room}</span>
            <span className="join-info-val">{room.name}</span>
          </div>
          <div className="join-info-row">
            <span className="join-info-key">{tj.host}</span>
            <span className="join-info-val">{room.host}</span>
          </div>
          <div className="join-info-row">
            <span className="join-info-key">{tj.mode}</span>
            <span className="join-info-val">{tj.classic}</span>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">{tj.yourName}</label>
          <input
            className="form-input"
            type="text"
            placeholder={tj.yourNamePlaceholder}
            value={yourName}
            onChange={e => setYourName(e.target.value)}
            maxLength={24}
          />
        </div>

        <button
          className="btn btn--primary"
          style={{ marginTop: 'auto' }}
          onClick={handleSubmit}
          disabled={!yourName.trim()}
        >
          {tj.submit}
        </button>
      </div>
    </div>
  );
}
