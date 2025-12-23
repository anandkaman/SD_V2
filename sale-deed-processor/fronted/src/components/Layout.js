import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon } from 'lucide-react';
import Footer from './Footer';
import '../styles/Layout.css';

const Layout = ({ children }) => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  return (
    <div className={`app-container ${theme}`}>
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <img src="/logo.png" alt="Income Tax Department - Sale Deed AI" className="logo-icon" />
            <h1>Sale Deed AI</h1>
          </div>

          <nav className="nav">
            <Link
              to="/control-panel"
              className={location.pathname === '/control-panel' ? 'active' : ''}
            >
              Control Panel
            </Link>
            <Link
              to="/data"
              className={location.pathname === '/data' ? 'active' : ''}
            >
              Data View
            </Link>
          </nav>

          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
        </div>
      </header>

      <main className="main-content">
        {children}
      </main>

      <Footer />
    </div>
  );
};

export default Layout;
