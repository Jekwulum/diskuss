import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import { initSocket, getSocket } from '../socket.conn';
import config from '../config';
import Chat from './Chat';

const ChatLayout = ({ user }) => {
  const navigate = useNavigate();
  const [discussions, setDiscussions] = useState([]);
  const [activeDiscussion, setActiveDiscussion] = useState(null);
  const [socketReady, setSocketReady] = useState(false);
  const [socket, setSocket] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true); // New state for sidebar visibility

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token || !user) {
      navigate("/login");
      return;
    }

    const socket = initSocket(token);
    if (socket) {
      socket.on("connect", () => {
        console.log("Connected to socket");
        setSocket(socket);
        setSocketReady(true);
      });

      socket.on("connect_error", (err) => {
        console.error("Socket error:", err.message);
      });
    }

    const fetchDiscussions = async () => {
      try {
        const response = await axios.get(`${config.apiUrl}/api/diskuss/discussions`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        setDiscussions(response.data.data);
      } catch (error) {
        console.error('Error fetching discussions:', error);
      }
    };

    fetchDiscussions();

    return () => {
      const activeSocket = getSocket();
      if (activeSocket) activeSocket.disconnect();
    };
  }, [user, navigate]);

  if (!socketReady) {
    return <div className="p-4 text-center">Connecting to chat...</div>;
  }

  return (
    <div className="relative flex h-screen">
      {/* Sidebar with sliding animation */}
      <aside
        className={`bg-white absolute lg:relative z-10 h-full transition-all duration-300 ease-in-out 
          ${sidebarOpen ? 'w-64 translate-x-0' : 'w-0 -translate-x-full lg:-translate-x-0 lg:w-12'}`}
      >
        {/* Toggle button - always visible */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-0 right-0 p-2 translate-x-full bg-blue-100 rounded-r-lg hover:bg-blue-200 lg:right-auto lg:left-full lg:translate-x-0"
        >
          {sidebarOpen ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M15.707 15.707a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414l5-5a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 15.707a1 1 0 010-1.414L14.586 10l-4.293-4.293a1 1 0 111.414-1.414l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </button>

        {/* Sidebar content */}
        <div className={`overflow-y-auto h-full ${!sidebarOpen && 'hidden'}`}>
          <h2 className="p-2 mb-4 text-xl font-bold">Discussions</h2>
          {discussions.map((disc) => {
            const otherParticipants = disc.participants.filter(p => p._id !== user._id);
            const names = otherParticipants.map(p => p.username).join(', ');
            const lastMsg = disc.last_message;

            return (
              <div
                key={disc._id}
                onClick={() => setActiveDiscussion(disc)}
                className={`p-2 mb-2 rounded cursor-pointer transition ${activeDiscussion?._id === disc._id ? 'bg-blue-300' : 'bg-blue-100 hover:bg-gray-200'}`}
              >
                <div className="font-semibold text-gray-800">@{names}</div>
                {lastMsg && (
                  <div className="text-sm text-gray-600 truncate">
                    {lastMsg.text}
                    <span className="block mt-1 text-xs text-gray-400">
                      {new Date(lastMsg.timestamp).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                      })}
                    </span>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1">
        {activeDiscussion ? (
          <Chat user={user} discussion={activeDiscussion} socket={socket} />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="p-4">Select a conversation</div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ChatLayout;