import React, { useState } from 'react';
import './landingPage.css';
import RegistrationPage from './registrationPage';
import { useLocation, useNavigate } from 'react-router-dom';

const LandingPage = () => {
    const [isRegistering, setIsRegistering] = useState(false);
    const [userName, setUserName] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleRegisterSuccess = (username) => {
        setIsRegistering(false);
        setUserName(username)
        navigate('/user', { state: { userName: username } });
    };

    const handleLogin = () => {
        const loginData = { username: userName, password : password };
        fetch('http://localhost:5001/api/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.token) {
                navigate('/user', { state: { userName } });
            }
            else {
                alert(data.message);
            }
        })
        .catch(err => console.error('Login failed:', err));
    };

    return (
        <div className={`landing-page ${isRegistering ? 'registration': 'user'}`}>
            <div className={`background ${isRegistering ? 'registration-background' :'user-background'}`} />
            {isRegistering ? (
                <RegistrationPage onRegisterSuccess={handleRegisterSuccess} setIsRegistering={setIsRegistering} />
            ) : (
                <div className="mode-container">
                    <header>
                        <h2>ProjectPath</h2>
                    </header>
                    <div>
                        <p>Sign into your account.</p>
                        <input
                            type="text"
                            placeholder="Email or Username"
                            className="input-field"
                            value={userName}
                            onChange={(e) => setUserName(e.target.value)}
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            className="input-field"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <button className="btn" onClick={handleLogin}>Login</button>
                        <div className="links">
                            <a href="#forgot-password">Forgot password?</a>
                            <a href="#sign-up" onClick={() => setIsRegistering(true)}>
                                First time user? Sign up to vote.
                            </a>
                        </div>
                    </div>
                    <footer>
                        &copy; 2024 Voting App. All rights reserved.
                    </footer>
                </div>
            )}
        </div>
    );
};

export default LandingPage;
