const Spinner = () => (
  <svg className="w-5 h-5 mr-3 text-white animate-spin" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" strokeWidth="4" stroke="currentColor" fill="none"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 1 1 16 0A8 8 0 0 1 4 12z"></path>
  </svg>
);

export default Spinner;