import { useState, useEffect } from 'react';
import Hero from './Hero';
import FeaturesSection from './FeaturesSection';
import HowItWorks from './HowItWorks';
import Integrations from './Integrations';
import SignupCTA from './SignupCTA';
import AuthModal from './AuthModal';
import './HomePage.css';

function HomePage({ isLoginModalOpen, onCloseLoginModal }) {
  const [authView, setAuthView] = useState('login');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Synchroniser avec la modal de login de la navbar
  useEffect(() => {
    if (isLoginModalOpen) {
      setAuthView('login');
      setIsModalOpen(true);
    }
  }, [isLoginModalOpen]);

  const handleOpenModal = (view) => {
    setAuthView(view);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
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
        onSwitchAuth={setAuthView}
      />
    </div>
  );
}

export default HomePage;
