import { useState } from 'react';

export default function CreateRoomPage({ t, onNavigate }) {
  const tc = t.create;
  const [yourName, setYourName] = useState('');
  const [roomName, setRoomName] = useState('');
  const [mode, setMode]         = useState('classic');

  function handleSubmit() {
    if (!yourName.trim() || !roomName.trim()) return;
    onNavigate('game', { yourName: yourName.trim(), roomName: roomName.trim(), mode });
  }

  return (
    <div className="page">
      <div className="page-header">
        <button className="page-back-btn" onClick={() => onNavigate('lobby')}>
          {tc.back}
        </button>
        <h1 className="page-title">{tc.title}</h1>
      </div>

      <div className="page-content">
        <div className="form-group">
          <label className="form-label">{tc.yourName}</label>
          <input
            className="form-input"
            type="text"
            placeholder={tc.yourNamePlaceholder}
            value={yourName}
            onChange={e => setYourName(e.target.value)}
            maxLength={24}
          />
        </div>

        <div className="form-group">
          <label className="form-label">{tc.roomName}</label>
          <input
            className="form-input"
            type="text"
            placeholder={tc.roomNamePlaceholder}
            value={roomName}
            onChange={e => setRoomName(e.target.value)}
            maxLength={32}
          />
        </div>

        <div className="form-group">
          <label className="form-label">{tc.gameMode}</label>
          <div className="form-select-wrap">
            <select
              className="form-select"
              value={mode}
              onChange={e => setMode(e.target.value)}
            >
              <option value="classic">{tc.classic}</option>
            </select>
          </div>
        </div>

        <button
          className="btn btn--primary"
          style={{ marginTop: 'auto' }}
          onClick={handleSubmit}
          disabled={!yourName.trim() || !roomName.trim()}
        >
          {tc.submit}
        </button>
      </div>
    </div>
  );
}
