import React, { useEffect, useState } from 'react';

const MessageInput = ({ socket, discussion_id, recipient_id, onNewMessage}) => {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!text.trim()) return;

    const messagePayload = { text, discussion_id, recipient_id };

    socket.emit('send_message', messagePayload);
    setText('');
    socket.emit('get_discussions', {discussion_id});
  };

  useEffect(() => {
    socket.on('get_discussions', (data) => {
      onNewMessage(data);
    });
  }, [onNewMessage, socket]);

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-2 p-2 border-t"
    >
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type a message..."
        className="flex-1 px-4 py-2 border rounded-full focus:outline-none"
      />
      <button
        type="submit"
        className="px-4 py-2 font-semibold text-white bg-blue-500 rounded-full hover:bg-blue-600"
      >
        Send
      </button>
    </form>
  );
};

export default MessageInput;
