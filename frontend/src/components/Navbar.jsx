import { useState } from 'react';
import './Navbar.css';
import Logo from './Logo';

function Navbar({ onScrollToSection, activeSection, onOpenLoginModal }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogoClick = () => {
    onScrollToSection('accueil');
    setIsMobileMenuOpen(false);
  };

  const handleNavClick = (section) => {
    if (section === 'login') {
      onOpenLoginModal();
    } else {
      onScrollToSection(section);
    }
    setIsMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
          <Logo size={32} />
        </div>

        {/* Hamburger Button */}
        <button 
          className={`navbar-hamburger ${isMobileMenuOpen ? 'active' : ''}`}
          onClick={toggleMobileMenu}
          aria-label="Menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div className={`navbar-menu ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          <button 
            className={`navbar-link ${activeSection === 'accueil' ? 'active' : ''}`}
            onClick={handleLogoClick}
          >
            Accueil
          </button>
          <button 
            className={`navbar-link ${activeSection === 'fonctionnalites' ? 'active' : ''}`}
            onClick={() => handleNavClick('fonctionnalites')}
          >
            Fonctionnalités
          </button>
          <button 
            className={`navbar-link ${activeSection === 'comment-ca-marche' ? 'active' : ''}`}
            onClick={() => handleNavClick('comment-ca-marche')}
          >
            Comment ça marche
          </button>
          <button 
            className={`navbar-link ${activeSection === 'integrations' ? 'active' : ''}`}
            onClick={() => handleNavClick('integrations')}
          >
            Intégrations
          </button>
          <button 
            className="navbar-btn"
            onClick={() => handleNavClick('login')}
          >
            Se connecter
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
