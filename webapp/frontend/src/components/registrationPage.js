import React, { useState } from 'react';
import './landingPage.css';

const RegistrationPage = ({ onRegisterSuccess, setIsRegistering }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');  // Added state for handling errors

    const handleRegister = () => {
        // Handle registration API call
        const userData = {
            username,
            email,
            password
        };

        fetch('http://localhost:5001/api/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
        .then(response => response.json())
        .then(data => {
            if (data._id) {  // Checking if the registration was successful
                onRegisterSuccess(username);
            } else {
                setError(data.message || 'Registration failed');  // Set error message if registration fails
            }
        })
        .catch(err => setError('Registration failed. Please try again.'));  // Handle any fetch errors
    };

    return (
        <div className="mode-container">
            <header>
                <h2>ProjectPath</h2>
            </header>
            <div>
                <h2>Register</h2>
                <p>Sign up to participate in the latest polls.</p>
                {error && <p style={{ color: 'red' }}>{error}</p>} 
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    className="input-field"
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="input-field"
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="input-field"
                />
                <button className="btn" onClick={handleRegister}>Register</button>
                <button className="toggle-btn" onClick={() => setIsRegistering(false)}>
                    Back to Login
                </button>
            </div>
            <footer>
                &copy; 2024 Voting App. All rights reserved.
            </footer>
        </div>
    );
};

export default RegistrationPage;
