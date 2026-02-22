import { useState } from 'react';
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
  
  // La modal est ouverte si la prop externe est true OU si l'état interne est true
  const isModalOpen = isLoginModalOpen || isInternalModalOpen;
  
  // Dériver authView : si la modal externe est ouverte, forcer 'login', sinon utiliser l'état interne
  const authView = isLoginModalOpen ? 'login' : internalAuthView;

  const handleOpenModal = (view) => {
    console.log('handleOpenModal called with view:', view);
    setInternalAuthView(view);
    setIsInternalModalOpen(true);
  };

  const handleCloseModal = () => {
    console.log('handleCloseModal called');
    setIsInternalModalOpen(false);
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
