import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
    const navigate = useNavigate();

    const features = [
        { icon: "⚡", title: "Instant Reasoning", desc: "Complex problem solving in seconds." },
        { icon: "🛠️", title: "Multi-Tool Support", desc: "Connect databases, APIs, and file systems." },
        { icon: "🎤", title: "Voice Control", desc: "Interact naturally with voice commands." }
    ];

    return (
        <div className="home-container">
            <div className="hero-section">
                <div className="hero-badge">Next-Gen AI Interface</div>
                <h1 className="hero-title">
                    The intelligence of the <br />
                    <span>NuraAgent</span> Ecosystem.
                </h1>
                <p className="hero-subtitle">
                    Experience a revolutionary way to interact with AI. Modular, fast, and designed for professionals who demand excellence.
                </p>
                
                <div className="hero-actions">
                    <button className="btn-primary" onClick={() => navigate('/chat')}>
                        Start a Conversation
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                    </button>
                    <button className="btn-secondary">
                        View Demo
                    </button>
                </div>
            </div>

            <div className="features-grid">
                {features.map((f, i) => (
                    <div key={i} className="feature-card">
                        <div className="f-icon">{f.icon}</div>
                        <h3>{f.title}</h3>
                        <p>{f.desc}</p>
                    </div>
                ))}
            </div>

            <div className="bottom-blob"></div>
            <div className="top-blob"></div>
        </div>
    );
};

export default HomePage;
