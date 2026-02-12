import { useState, useEffect } from 'react';
import Navbar from './Navbar';
import HomePage from './HomePage';
import Footer from './Footer';

function AuthView() {
  const [activeSection, setActiveSection] = useState('accueil');
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const sections = ['accueil', 'fonctionnalites', 'comment-ca-marche', 'integrations'];
      const scrollPosition = window.scrollY + 150; // Offset for navbar

      // Check if at top of page
      if (window.scrollY < 100) {
        setActiveSection('accueil');
        return;
      }

      // Find which section is currently in view
      for (const sectionId of sections) {
        const element = document.getElementById(sectionId);
        if (element) {
          const { offsetTop, offsetHeight } = element;
          if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
            setActiveSection(sectionId);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial check

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleScrollToSection = (sectionId) => {
    if (sectionId === 'accueil') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      setActiveSection('accueil');
      return;
    }

    const element = document.getElementById(sectionId);
    if (element) {
      const offset = 80; // Height of fixed navbar
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="app">
      <Navbar 
        onScrollToSection={handleScrollToSection} 
        activeSection={activeSection}
        onOpenLoginModal={() => setIsLoginModalOpen(true)}
      />
      <HomePage 
        isLoginModalOpen={isLoginModalOpen}
        onCloseLoginModal={() => setIsLoginModalOpen(false)}
      />
      <Footer />
    </div>
  );
}

export default AuthView;
