import React from 'react';

const Logo = ({ className = "w-12 h-12" }) => {
  return (
    <svg 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Document Base */}
      <path 
        d="M6 3H14L18 7V21H6V3Z" 
        stroke="currentColor" 
        strokeWidth="1.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        className="text-indigo-400"
      />
      {/* Brain/Neural Patterns within the document */}
      <path 
        d="M9 11C9 9.89543 9.89543 9 11 9C12.1046 9 13 9.89543 13 11" 
        stroke="currentColor" 
        strokeWidth="1.2" 
        strokeLinecap="round"
        className="text-purple-400"
      />
      <path 
        d="M10 14C10 12.8954 10.8954 12 12 12C13.1046 12 14 12.8954 14 14" 
        stroke="currentColor" 
        strokeWidth="1.2" 
        strokeLinecap="round"
        className="text-indigo-300"
      />
      <circle cx="11" cy="11" r="1" fill="currentColor" className="text-purple-500" />
      <circle cx="13" cy="14" r="1" fill="currentColor" className="text-indigo-500" />
      
      {/* Corner Fold */}
      <path 
        d="M14 3V7H18" 
        stroke="currentColor" 
        strokeWidth="1.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        className="text-indigo-400/50"
      />
    </svg>
  );
};

export default Logo;
