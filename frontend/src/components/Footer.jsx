import React from 'react';

function Footer() {
  return (
    <footer style={{
      textAlign: 'center',
      padding: '3rem 1rem',
      marginTop: '4rem',
      borderTop: '1px solid rgba(148, 163, 184, 0.1)',
       background:'rgb(226, 230, 250)' 
    }}>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        © 2026 PhishGuard AI - Advanced Phishing Detection System
      </p>
    </footer>
  );
}

export default Footer;
