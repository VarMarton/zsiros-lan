// Manages the single WebSocket connection to the backend.

const WS_URL = import.meta.env.VITE_WS_URL ?? `ws://${window.location.hostname}:8000/ws`;

let socket = null;
const listeners = new Map();

export function connect() {
  if (socket && socket.readyState === WebSocket.OPEN) return;

  socket = new WebSocket(WS_URL);

  socket.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    const handler = listeners.get(msg.type);
    if (handler) handler(msg);
    const catchAll = listeners.get("*");
    if (catchAll) catchAll(msg);
  };

  socket.onclose = () => {
    const handler = listeners.get("disconnected");
    if (handler) handler();
  };
}

export function send(msg) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error("WebSocket is not connected");
    return;
  }
  socket.send(JSON.stringify(msg));
}

export function on(type, handler) {
  listeners.set(type, handler);
}

export function off(type) {
  listeners.delete(type);
}

export function disconnect() {
  socket?.close();
  socket = null;
}
