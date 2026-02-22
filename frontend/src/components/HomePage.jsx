import { useState, useEffect } from 'react';
import Hero from './Hero';
import FeaturesSection from './FeaturesSection';
import HowItWorks from './HowItWorks';
import Integrations from './Integrations';
import SignupCTA from './SignupCTA';
import AuthModal from './AuthModal';
import './HomePage.css';

function HomePage({ isLoginModalOpen, onCloseLoginModal }) {
  const [internalAuthView, setInternalAuthView] = useState('login');
  const [isInternalModalOpen, setIsInternalModalOpen] = useState(false);
  
  console.log('HomePage render:', { isLoginModalOpen, isInternalModalOpen, internalAuthView });
  
  // Reset to login view when external modal opens
  useEffect(() => {
    if (isLoginModalOpen) {
      setInternalAuthView('login');
    }
  }, [isLoginModalOpen]);
  
  // La modal est ouverte si la prop externe est true OU si l'état interne est true
  const isModalOpen = isLoginModalOpen || isInternalModalOpen;
  
  // Use internalAuthView regardless of which modal trigger was used
  const authView = internalAuthView;

  const handleOpenModal = (view) => {
    console.log('handleOpenModal called with view:', view);
    setInternalAuthView(view);
    setIsInternalModalOpen(true);
  };

  const handleCloseModal = () => {
    console.log('handleCloseModal called');
    setIsInternalModalOpen(false);
    // Reset to login view when closing
    setInternalAuthView('login');
    if (onCloseLoginModal) {
      onCloseLoginModal();
    }
  };

  return (
    <div className="homepage">
      <div id="accueil">
        <Hero />
      </div>
      
      {/* Section Fonctionnalités */}
      <section id="fonctionnalites" className="section-features">
        <FeaturesSection />
      </section>
      
      {/* Section Comment ça marche */}
      <section id="comment-ca-marche" className="section-how-it-works">
        <HowItWorks />
      </section>
      
      {/* Section Intégrations */}
      <section id="integrations" className="section-integrations">
        <Integrations onOpenModal={() => handleOpenModal('login')} />
      </section>
      
      {/* Section CTA Signup */}
      <SignupCTA onSwitchToRegister={() => handleOpenModal('register')} />
      
      {/* Modal d'authentification */}
      <AuthModal 
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        authView={authView}
        onSwitchAuth={setInternalAuthView}
      />
    </div>
  );
}

export default HomePage;
