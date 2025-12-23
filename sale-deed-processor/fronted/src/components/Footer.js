import React, { useState, useEffect } from 'react';
import { Activity, Server, CheckCircle, XCircle } from 'lucide-react';
import api from '../services/api';
import '../styles/Footer.css';

const Footer = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [folderStats, setFolderStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemData();
    fetchFolderStats();

    // Poll health check every 2 minutes
    const systemInterval = setInterval(fetchSystemData, 120000);

    // Poll folder stats every 30 seconds
    const folderInterval = setInterval(fetchFolderStats, 30000);

    return () => {
      clearInterval(systemInterval);
      clearInterval(folderInterval);
    };
  }, []);

  const fetchSystemData = async () => {
    try {
      const health = await api.healthCheck().catch(() => null);
      setHealthStatus(health);
    } catch (error) {
      console.error('Error fetching health status:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFolderStats = async () => {
    try {
      const folders = await api.getFolderStats().catch(() => null);
      setFolderStats(folders);
    } catch (error) {
      console.error('Error fetching folder stats:', error);
    }
  };

  const StatusIcon = ({ status }) => {
    return status ? (
      <CheckCircle size={16} className="status-icon success" />
    ) : (
      <XCircle size={16} className="status-icon error" />
    );
  };

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <div className="footer-title">
            <Activity size={18} />
            <span>Health Status</span>
          </div>
          {loading ? (
            <span className="loading">Loading...</span>
          ) : (
            <div className="status-grid">
              <div className="status-item">
                <StatusIcon status={healthStatus?.status === 'healthy'} />
                <span>API: {healthStatus?.status || 'Unknown'}</span>
              </div>
            </div>
          )}
        </div>

        {/* System Info section hidden */}

        <div className="footer-section">
          <div className="footer-title">
            <Server size={18} />
            <span>Folder Statistics</span>
          </div>
          {loading ? (
            <span className="loading">Loading...</span>
          ) : folderStats ? (
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Newly Uploaded:</span>
                <span className="stat-value">{folderStats.newly_uploaded}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Processed:</span>
                <span className="stat-value">{folderStats.processed}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Failed:</span>
                <span className="stat-value">{folderStats.failed}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Left Over Reg Fee:</span>
                <span className="stat-value">{folderStats.left_over_reg_fee}</span>
              </div>
            </div>
          ) : (
            <span className="error-text">Folder stats unavailable</span>
          )}
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; 2025 SaleDeed AI. By Formonex Solutions Pvt Ltd,All rights reserved.</p>
             <p>&copy; Version 1.1.0</p>   
      </div>
    </footer>
  );
};

export default Footer;
