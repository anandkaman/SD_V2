import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout';
import ControlPanel from './pages/ControlPanel';
import DataView from './pages/DataView';
import './styles/App.css';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/control-panel" replace />} />
            <Route path="/control-panel" element={<ControlPanel />} />
            <Route path="/data" element={<DataView />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
