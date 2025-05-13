import React, { useRef, useState, useEffect } from 'react';
import MessageInput from './MessageInput';

const Chat = ({ discussion, user, socket }) => {
  const socketRef = useRef(null);
  const bottomRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [limit] = useState(5);
  const [offset] = useState(0);
  const [loading, setLoading] = useState(true);
  const discussion_id = discussion._id;

  useEffect(() => {
    socketRef.current = socket;

    if (!socketRef.current) {
      console.error('Socket is not connected');
      return;
    }

    socket.emit('get_discussion_messages', {
      discussion_id,
      limit,
      offset,
    });

    socket.on('get_discussion_messages', (data) => {
      setMessages(data);
      setLoading(false);
    });

    // Clean up listener
    return () => {
      socket.off('get_discussion_messages');
    };
  }, [discussion_id, limit, offset, socket]);

  // Scroll to bottom when messages update
  useEffect(() => {
    if (!loading) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [socket, messages, loading]);

  useEffect(() => {
    if (!socket) return;

    const handleReceiveMessage = (message) => {
      console.log("Received message:", message.data);
      setMessages((prevMessages) => [...message.data]);
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    socket.on("receive_message", handleReceiveMessage);

  }, [socket]);

  return (
    <div className="flex flex-col h-full p-4">
      <h2 className="mb-2 text-xl font-semibold">Messages</h2>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="flex-1 p-4 space-y-2 overflow-y-auto">
          {messages.map((msg) => {
            const isSender = msg.sender_id === user._id;

            return (
              <div
                key={msg._id}
                className={`flex ${isSender ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`
                    p-3 
                    rounded-lg 
                    max-w-xs 
                    break-words 
                    ${isSender
                      ? 'bg-red-100 border-r-4 border-red-500 text-red-800 rounded-br-none'
                      : 'bg-blue-100 border-l-4 border-blue-500 text-blue-800 rounded-bl-none'}
                  `}
                >
                  <p>{msg.text}</p>
                  <div className="mt-1 text-xs text-gray-500">
                    {new Date(msg.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            );
          })}
          {/* Invisible div to scroll into view */}
          <div ref={bottomRef} />
        </div>
      )}

      <MessageInput
        socket={socket}
        discussion_id={discussion_id}
        recipient_id={discussion.participants.find(p => p._id !== user._id)._id}
      />
    </div>
  );
};

export default Chat;
