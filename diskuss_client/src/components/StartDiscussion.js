import React, { useEffect, useState } from 'react';
import axios from 'axios';
import config from '../config';

const StartDiscussion = ({ user, isOpen, setIsOpen, onDiscussionCreated }) => {
  const [participants, setParticipants] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (query) => {
    if (query.length < 2) return;
    setLoading(true);
    try {
      const response = await axios.get(`${config.apiUrl}/api/diskuss/users?username=${query}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      console.log(response.data.data);
      setSearchResults(response.data.data.filter(u => u._id !== user._id));
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const createDiscussion = async () => {
    if (participants.length === 0) return;

    try {
      const response = await axios.post(`${config.apiUrl}/api/diskuss/discussions`, {
        participants: participants.map(p => p._id)
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      onDiscussionCreated(response.data.data);
      setIsOpen(false);
      setParticipants([]);
    } catch (error) {
      console.error('Create discussion error:', error);
    }
  };

  return (
    <div className="relative">

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md p-6 bg-white rounded-lg">
            <h2 className="mb-4 text-xl font-bold">Start New Discussion</h2>

            {/* Search Input */}
            <div className="relative mb-4">
              <input
                type="text"
                placeholder="Search users..."
                className="w-full p-2 border rounded"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  handleSearch(e.target.value);
                }}
              />
              {loading && (
                <div className="absolute right-3 top-3">
                  <div className="w-4 h-4 border-b-2 border-gray-900 rounded-full animate-spin"></div>
                </div>
              )}
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mb-4 overflow-y-auto max-h-40">
                {searchResults.map(user => (
                  <div
                    key={user._id}
                    className="flex items-center p-2 cursor-pointer hover:bg-gray-100"
                    onClick={() => {
                      if (!participants.some(p => p._id === user._id)) {
                        setParticipants([...participants, user]);
                      }
                      setSearchQuery('');
                      setSearchResults([]);
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-linecap="round" stroke-linejoin="round" width="28" height="28" stroke-width="2"> <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"></path> <path d="M12 10m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"></path> <path d="M6.168 18.849a4 4 0 0 1 3.832 -2.849h4a4 4 0 0 1 3.834 2.855"></path> </svg>
                    <span className='ml-1'>@{user.username}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Selected Participants */}
            {participants.length > 0 && (
              <div className="mb-4">
                <h3 className="mb-2 font-medium">Participants:</h3>
                <div className="flex flex-wrap gap-2">
                  {participants.map(user => (
                    <div key={user._id} className="flex items-center px-2 py-1 bg-gray-100 rounded">
                      <span className="mr-1">@{user.username}</span>
                      <button
                        onClick={() => setParticipants(participants.filter(p => p._id !== user._id))}
                        className="text-red-500"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-start gap-2">
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 border rounded"
              >
                Cancel
              </button>
              <button
                onClick={createDiscussion}
                disabled={participants.length === 0}
                className={`px-4 py-2 rounded text-white ${participants.length === 0 ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'}`}
              >
                Start Discussion
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StartDiscussion;