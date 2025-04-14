import React from 'react';

function Header() {
  return (
    <header className="header">
      <div className="logo">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      <h1>Competitive Intelligence Assistant</h1>
    </header>
  );
}

export default Header;