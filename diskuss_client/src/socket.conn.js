import { io } from 'socket.io-client';
import config from './config';

let socket = null;

export const initSocket = (token) => {
  if (!token) return null;

  if (socket && socket.connected) {
    socket.disconnect();
  }

  socket = io(config.socketUrl, {
    auth: { token },
    transports: ["websocket"],
    autoConnect: true,
  });

  socket.on("connect", () => {
    console.log("Socket connected:", socket.id);
  });

  socket.on("connect_error", (err) => {
    console.error("Socket connection error:", err.message);
  });

  socket.on("disconnect", (reason) => {
    console.warn("Socket disconnected:", reason);
  });

  return socket;
};

export const getSocket = () => socket;