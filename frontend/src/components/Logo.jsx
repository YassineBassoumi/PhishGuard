import React from 'react';
import './Logo.css';

function Logo({ size = 32, showText = true, className = '' }) {
  const containerSize = size * 1.25; // 40px pour size=32
  const shieldSize = size * 0.75; // 24px pour size=32
  const fontSize = size * 0.625; // 20px pour size=32

  return (
    <div className={`logo-container ${className}`}>
      {/* Shield Container with Gradient Background */}
      <div 
        className="shield-container"
        style={{
          width: `${containerSize}px`,
          height: `${containerSize}px`,
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #5b8def 0%, #9b7ee8 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(91, 141, 239, 0.3)'
        }}
      >
        {/* Shield Icon */}
        <svg width={shieldSize} height={shieldSize} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z"
            fill="white"
            stroke="white"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      
      {/* Text Logo */}
      {showText && (
        <span style={{
          fontSize: `${fontSize}px`,
          fontWeight: 700,
          color: '#3b4b65f1',
          userSelect: 'none'
        }}>
          Phish<span style={{ color: '#5b8def' }}>Guard</span>
        </span>
      )}
    </div>
  );
}

export default Logo;
