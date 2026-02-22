import './SignupCTA.css';

function SignupCTA({ onSwitchToRegister }) {
  const handleSignupClick = () => {
    console.log('SignupCTA button clicked');
    console.log('onSwitchToRegister:', onSwitchToRegister);
    // Ouvrir la modal d'inscription
    if (onSwitchToRegister) {
      onSwitchToRegister();
    } else {
      console.error('onSwitchToRegister is undefined!');
    }
  };

  return (
    <div className="signup-cta">
      <div className="signup-cta-content">
        <h2 className="signup-cta-title">
          Prêt à sécuriser vos <span className="signup-cta-highlight">emails</span> ?
        </h2>
        <p className="signup-cta-text">
           Protégez-vous dès aujourd’hui contre les attaques de phishing.
    Analyse intelligente et protection en temps réel.
        </p>
        <div className="signup-cta-buttons">
          <button className="signup-btn-primary" onClick={handleSignupClick}>
            Créer un compte gratuit →
          </button>
         
        </div>
      </div>
    </div>
  );
}

export default SignupCTA;
