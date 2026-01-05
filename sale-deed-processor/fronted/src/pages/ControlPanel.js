import React, { useState, useEffect, useCallback } from 'react';
import Joyride, { STATUS } from 'react-joyride';
import {
  Upload,
  Play,
  Square,
  Eye,
  Download,
  FileText,
  Loader,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Package,
  Search,
  HelpCircle,
  Bell,
} from 'lucide-react';
import api from '../services/api';
import { controlPanelSteps, joyrideStyles } from '../config/tourSteps';
import { useNotifications } from '../context/NotificationContext';
import NotificationCenter from '../components/NotificationCenter';
import ToastNotification from '../components/ToastNotification';
import '../styles/ControlPanel.css';

const ControlPanel = () => {
  // Format date to DD/MM/YYYY, HH:MM:SS AM/PM in IST (Indian Standard Time)
  const formatDateIST = (dateString) => {
    if (!dateString) return '-';

    // Parse the UTC datetime string from backend
    const utcDate = new Date(dateString);

    // Check if date is valid
    if (isNaN(utcDate.getTime())) return '-';

    // Use Intl.DateTimeFormat for reliable timezone conversion
    const formatter = new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });

    const parts = formatter.formatToParts(utcDate);
    const get = (type) => parts.find(p => p.type === type)?.value || '';

    const day = get('day');
    const month = get('month');
    const year = get('year');
    let hours = parseInt(get('hour'));
    const minutes = get('minute');
    const seconds = get('second');

    // Convert to 12-hour format
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const hoursStr = String(hours).padStart(2, '0');

    return `${day}/${month}/${year}, ${hoursStr}:${minutes}:${seconds} ${ampm}`;
  };

  // Helper function to get batch name from batch_id
  const getBatchName = (batchId) => {
    if (!batchId) return 'N/A';
    const batch = recentBatches.find(b => b.batch_id === batchId);
    return batch ? (batch.batch_name || batchId) : batchId;
  };

  // Notification hook
  const { unreadCount, setShowNotificationCenter } = useNotifications();

  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [processingStats, setProcessingStats] = useState(null);
  const [visionStats, setVisionStats] = useState(null);
  const [folderStats, setFolderStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [workerCount, setWorkerCount] = useState(2); // Default: 2 workers (legacy)
  const [ocrWorkers, setOcrWorkers] = useState(5);  // OCR workers
  const [llmWorkers, setLlmWorkers] = useState(5);  // LLM workers
  const [stage2QueueSize, setStage2QueueSize] = useState(2);  // Stage-2 queue size
  const [enableOcrMultiprocessing, setEnableOcrMultiprocessing] = useState(false);  // OCR multiprocessing
  const [ocrPageWorkers, setOcrPageWorkers] = useState(2);  // OCR page workers
  const [useEmbeddedOcr, setUseEmbeddedOcr] = useState(false);  // Embedded OCR mode
  const [systemConfig, setSystemConfig] = useState(null);  // System configuration

  // Batch tracking states
  const [currentBatchId, setCurrentBatchId] = useState(null);
  const [recentBatches, setRecentBatches] = useState([]);
  const [showAllBatches, setShowAllBatches] = useState(false);
  const [batchSearchTerm, setBatchSearchTerm] = useState('');

  // Manual tracking for stop button states (always enabled once started)
  const [isPdfProcessingActive, setIsPdfProcessingActive] = useState(false);
  const [isVisionProcessingActive, setIsVisionProcessingActive] = useState(false);

  // User Info Modal States
  const [showUserInfoModal, setShowUserInfoModal] = useState(false);
  const [userInfo, setUserInfo] = useState({
    userName: '',
    numberOfFiles: '',
    fileRegion: '',
    date: new Date().toISOString().split('T')[0], // System date in YYYY-MM-DD format
  });

  // Ticket System States
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [ticketForm, setTicketForm] = useState({
    userName: '',
    batchId: '',
    errorType: '',
    description: '',
  });
  const [ticketBatchSearchTerm, setTicketBatchSearchTerm] = useState('');

  // Tour Guide States
  const [runTour, setRunTour] = useState(false);

  // Management Modals States
  const [showUserRecordsModal, setShowUserRecordsModal] = useState(false);
  const [showTicketsManagementModal, setShowTicketsManagementModal] = useState(false);
  const [userRecords, setUserRecords] = useState([]);
  const [allTickets, setAllTickets] = useState([]);
  const [userRecordsSearchTerm, setUserRecordsSearchTerm] = useState('');
  const [ticketsSearchTerm, setTicketsSearchTerm] = useState('');

  // Failed Documents Modal States
  const [showFailedModal, setShowFailedModal] = useState(false);
  const [failedDocuments, setFailedDocuments] = useState(null);
  const [expandedBatches, setExpandedBatches] = useState(new Set());

  // Define callback functions first
  const fetchStats = useCallback(async () => {
    try {
      const [procStats, visStats, fStats] = await Promise.all([
        api.getProcessingStats().catch(() => null),
        api.getVisionStats().catch(() => null),
        api.getFolderStats().catch(() => null),
      ]);
      setProcessingStats(procStats);
      setVisionStats(visStats);
      setFolderStats(fStats);

      // Update manual tracking based on backend status
      if (procStats && !procStats.is_running && isPdfProcessingActive) {
        setIsPdfProcessingActive(false);
      }
      if (visStats && !visStats.is_running && isVisionProcessingActive) {
        setIsVisionProcessingActive(false);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  }, [isPdfProcessingActive, isVisionProcessingActive]);

  const fetchSystemConfig = useCallback(async () => {
    try {
      const sysConfig = await api.getSystemConfig();
      if (sysConfig) {
        setSystemConfig(sysConfig);
        setOcrWorkers(sysConfig.max_ocr_workers || 5);
        setLlmWorkers(sysConfig.max_llm_workers || 5);
        setStage2QueueSize(sysConfig.stage2_queue_size || 2);
        setEnableOcrMultiprocessing(sysConfig.enable_ocr_multiprocessing || false);
        setOcrPageWorkers(sysConfig.ocr_page_workers || 2);
        setUseEmbeddedOcr(sysConfig.use_embedded_ocr || false);
      }
    } catch (err) {
      console.error('Error fetching system config:', err);
    }
  }, []);

  const fetchActiveStats = useCallback(async () => {
    try {
      const [procStats, visStats] = await Promise.all([
        api.getProcessingStats().catch(() => null),
        api.getVisionStats().catch(() => null),
      ]);
      if (procStats) {
        setProcessingStats(procStats);
        // Auto-disable stop button when backend reports not running
        if (!procStats.is_running && isPdfProcessingActive) {
          setIsPdfProcessingActive(false);
        }
      }
      if (visStats) {
        setVisionStats(visStats);
        // Auto-disable stop button when backend reports not running
        if (!visStats.is_running && isVisionProcessingActive) {
          setIsVisionProcessingActive(false);
        }
      }
    } catch (err) {
      console.error('Error fetching active stats:', err);
    }
  }, [isPdfProcessingActive, isVisionProcessingActive]);

  const fetchFolderStats = useCallback(async () => {
    try {
      const fStats = await api.getFolderStats().catch(() => null);
      if (fStats) setFolderStats(fStats);
    } catch (err) {
      console.error('Error fetching folder stats:', err);
    }
  }, []);

  const fetchBatches = useCallback(async () => {
    try {
      const batches = await api.getBatches();
      setRecentBatches(batches || []);
    } catch (err) {
      console.error('Error fetching batches:', err);
    }
  }, []);

  // Initial fetch - load system config only once
  useEffect(() => {
    fetchSystemConfig();
  }, [fetchSystemConfig]);

  // Initial stats fetch
  useEffect(() => {
    fetchStats();
    fetchBatches();
  }, [fetchStats, fetchBatches]);

  // Polling - only when processing is active
  useEffect(() => {
    const isPdfProcessing = processingStats?.is_running || isPdfProcessingActive;
    const isVisionProcessing = visionStats?.is_running || isVisionProcessingActive;

    if (isPdfProcessing || isVisionProcessing) {
      // Immediate fetch
      fetchActiveStats();

      // Poll active stats every 5 seconds while processing
      const activeStatsInterval = setInterval(fetchActiveStats, 5000);

      return () => {
        clearInterval(activeStatsInterval);
      };
    }
    // No polling when idle - stats are only fetched on user actions
  }, [processingStats?.is_running, visionStats?.is_running, isPdfProcessingActive, isVisionProcessingActive, fetchActiveStats]);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files).filter((file) =>
      file.name.toLowerCase().endsWith('.pdf')
    );
    setSelectedFiles(files);
    setUploadStatus(null);
    setError(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const droppedFiles = Array.from(e.dataTransfer.files).filter((file) =>
      file.name.toLowerCase().endsWith('.pdf')
    );

    if (droppedFiles.length > 0) {
      setSelectedFiles(droppedFiles);
      setUploadStatus(null);
      setError(null);
    }
  };

  const handleUploadClick = () => {
    if (selectedFiles.length === 0) {
      setError('Please select PDF files to upload');
      return;
    }
    // Auto-fill number of files based on selected files
    setUserInfo(prev => ({
      ...prev,
      numberOfFiles: selectedFiles.length
    }));
    // Show User Info modal before upload
    setShowUserInfoModal(true);
  };

  const handleUserInfoSubmit = async () => {
    // Validate user info
    if (!userInfo.userName.trim()) {
      setError('Please enter your name');
      return;
    }
    if (!userInfo.numberOfFiles || userInfo.numberOfFiles <= 0) {
      setError('Please enter a valid number of files');
      return;
    }
    if (!userInfo.fileRegion.trim()) {
      setError('Please enter file region/location');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // First, save user info
      const userInfoData = {
        user_name: userInfo.userName,
        number_of_files: parseInt(userInfo.numberOfFiles),
        file_region: userInfo.fileRegion,
        batch_id: null, // Will be updated after upload
      };

      await api.createUserInfo(userInfoData);

      // Then proceed with upload
      const result = await api.uploadPDFs(selectedFiles);
      setUploadStatus(result);
      setCurrentBatchId(result.batch_id);

      // Update user info with batch_id
      await api.updateUserInfoBatch(result.batch_id, userInfo.userName);

      setSelectedFiles([]);
      // Reset file input
      document.getElementById('file-input').value = '';

      // Reset user info form
      setUserInfo({
        userName: '',
        numberOfFiles: '',
        fileRegion: '',
        date: new Date().toISOString().split('T')[0],
      });

      // Close modal
      setShowUserInfoModal(false);

      // Refresh folder stats and batches after upload
      await fetchFolderStats();
      await fetchBatches();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleUserInfoCancel = () => {
    setShowUserInfoModal(false);
    setError(null);
  };

  const handleOpenTicketModal = () => {
    setShowTicketModal(true);
    setError(null);
  };

  const handleTicketSubmit = async () => {
    // Validate ticket form
    if (!ticketForm.userName.trim()) {
      setError('Please enter your name');
      return;
    }
    if (!ticketForm.batchId) {
      setError('Please select a batch');
      return;
    }
    if (!ticketForm.errorType.trim()) {
      setError('Please enter error type');
      return;
    }
    if (!ticketForm.description.trim()) {
      setError('Please enter a description');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const ticketData = {
        user_name: ticketForm.userName,
        batch_id: ticketForm.batchId,
        error_type: ticketForm.errorType,
        description: ticketForm.description,
      };

      await api.createTicket(ticketData);

      // Reset form
      setTicketForm({
        userName: '',
        batchId: '',
        errorType: '',
        description: '',
      });

      // Close modal
      setShowTicketModal(false);

      // Show success message
      setUploadStatus({
        success: true,
        message: 'Ticket submitted successfully',
        type: 'ticket-created',
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit ticket');
    } finally {
      setLoading(false);
    }
  };

  const handleTicketCancel = () => {
    setShowTicketModal(false);
    setError(null);
    setTicketBatchSearchTerm('');
  };

  const handleOpenUserRecordsModal = async () => {
    setLoading(true);
    try {
      const records = await api.getAllUserInfo();
      setUserRecords(records || []);
      setShowUserRecordsModal(true);
    } catch (err) {
      setError('Failed to load user records');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseUserRecordsModal = () => {
    setShowUserRecordsModal(false);
    setUserRecordsSearchTerm('');
  };

  const handleOpenTicketsManagementModal = async () => {
    setLoading(true);
    try {
      const tickets = await api.getAllTickets();
      setAllTickets(tickets || []);
      setShowTicketsManagementModal(true);
    } catch (err) {
      setError('Failed to load tickets');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseTicketsManagementModal = () => {
    setShowTicketsManagementModal(false);
    setTicketsSearchTerm('');
  };

  const handleUpdateTicketStatus = async (ticketId, newStatus) => {
    setLoading(true);
    try {
      await api.updateTicketStatus(ticketId, newStatus);
      // Refresh tickets list
      const tickets = await api.getAllTickets();
      setAllTickets(tickets || []);
      setUploadStatus({
        success: true,
        message: `Ticket status updated to ${newStatus}`,
        type: 'ticket-updated',
      });
    } catch (err) {
      setError('Failed to update ticket status');
    } finally {
      setLoading(false);
    }
  };

  // Tour Guide Handlers
  const handleStartTour = () => {
    setRunTour(true);
  };

  const handleJoyrideCallback = (data) => {
    const { status } = data;

    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRunTour(false);
    }
  };

  const handleStartProcessing = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.startProcessing(
        ocrWorkers,
        llmWorkers,
        stage2QueueSize,
        enableOcrMultiprocessing,
        ocrPageWorkers
      );
      if (result.success) {
        setUploadStatus({ ...result, type: 'processing' });
        setIsPdfProcessingActive(true); // Enable stop button
        // Immediate fetch to update stats
        await fetchActiveStats();
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start processing');
    } finally {
      setLoading(false);
    }
  };

  const increaseWorkers = () => {
    setWorkerCount(prev => Math.min(prev + 1, 5));
  };

  const decreaseWorkers = () => {
    setWorkerCount(prev => Math.max(prev - 1, 1));
  };

  const increaseOcrWorkers = () => {
    setOcrWorkers(prev => Math.min(prev + 1, 20));
  };

  const decreaseOcrWorkers = () => {
    setOcrWorkers(prev => Math.max(prev - 1, 1));
  };

  const increaseLlmWorkers = () => {
    setLlmWorkers(prev => Math.min(prev + 1, 20));
  };

  const decreaseLlmWorkers = () => {
    setLlmWorkers(prev => Math.max(prev - 1, 1));
  };

  const increaseQueueSize = () => {
    setStage2QueueSize(prev => Math.min(prev + 1, 10));
  };

  const decreaseQueueSize = () => {
    setStage2QueueSize(prev => Math.max(prev - 1, 1));
  };

  const increaseOcrPageWorkers = () => {
    setOcrPageWorkers(prev => Math.min(prev + 1, 8));
  };

  const decreaseOcrPageWorkers = () => {
    setOcrPageWorkers(prev => Math.max(prev - 1, 1));
  };

  const handleStopProcessing = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.stopProcessing();
      setUploadStatus({ ...result, type: 'stop' });
      setIsPdfProcessingActive(false); // Disable stop button
      // Refresh stats after stopping
      await fetchStats();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop processing');
    } finally {
      setLoading(false);
    }
  };

  const handleStartVision = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.startVisionProcessing();
      if (result.success) {
        setUploadStatus({ ...result, type: 'vision' });
        setIsVisionProcessingActive(true); // Enable stop button
        // Immediate fetch to update stats
        await fetchActiveStats();
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start vision processing');
    } finally {
      setLoading(false);
    }
  };

  const handleStopVision = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.stopVisionProcessing();
      setUploadStatus({ ...result, type: 'stop-vision' });
      setIsVisionProcessingActive(false); // Disable stop button
      // Refresh stats after stopping
      await fetchStats();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop vision processing');
    } finally {
      setLoading(false);
    }
  };

  const handleRerunFailed = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.rerunFailedPDFs();
      if (result.success) {
        setUploadStatus({ ...result, type: 'rerun-failed' });
        await fetchStats(); // Refresh stats after rerunning

        // Automatically start processing the failed PDFs
        const startResult = await api.startProcessing();
        if (startResult.success) {
          setUploadStatus({
            ...startResult,
            message: `${result.message}. Processing started automatically.`,
            type: 'rerun-and-process'
          });
          setIsPdfProcessingActive(true); // Enable stop button
        }
      } else {
        setError(result.message || 'No failed PDFs to rerun');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to rerun failed PDFs');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadFailed = async () => {
    setLoading(true);
    setError(null);
    try {
      const blob = await api.downloadFailedPDFs();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `failed_pdfs_${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setUploadStatus({
        success: true,
        message: 'Failed PDFs downloaded successfully',
        type: 'download-failed'
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to download failed PDFs');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEmbeddedOcr = async (enabled) => {
    try {
      const response = await api.toggleEmbeddedOcr(enabled);
      setUseEmbeddedOcr(enabled);
      setUploadStatus({
        success: true,
        message: response.message,
        type: 'toggle-ocr'
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to toggle embedded OCR');
      // Revert the checkbox state on error
      setUseEmbeddedOcr(!enabled);
    }
  };

  // Failed Documents Handlers
  const fetchFailedDocuments = async () => {
    try {
      const data = await api.getFailedDocuments();
      setFailedDocuments(data);
    } catch (err) {
      setError('Failed to fetch failed documents');
    }
  };

  const handleViewFailedDocuments = async () => {
    setLoading(true);
    try {
      await fetchFailedDocuments();
      setShowFailedModal(true);
    } catch (err) {
      setError('Failed to load failed documents');
    } finally {
      setLoading(false);
    }
  };

  const handleRerunFailedBatch = async (batchId) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.rerunFailedBatch(batchId);
      if (result.success) {
        setUploadStatus({ ...result, type: 'rerun-batch' });
        await fetchStats(); // Refresh stats
        await fetchFailedDocuments(); // Refresh failed docs list
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to rerun batch');
    } finally {
      setLoading(false);
    }
  };

  const toggleBatchExpansion = (batchId) => {
    const newExpanded = new Set(expandedBatches);
    if (newExpanded.has(batchId)) {
      newExpanded.delete(batchId);
    } else {
      newExpanded.add(batchId);
    }
    setExpandedBatches(newExpanded);
  };

  const ProgressBar = ({ value, max, label }) => {
    const percentage = max > 0 ? (value / max) * 100 : 0;
    return (
      <div className="progress-container">
        <div className="progress-label">
          <span>{label}</span>
          <span>
            {value} / {max} ({percentage.toFixed(1)}%)
          </span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${percentage}%` }} />
        </div>
      </div>
    );
  };

  return (
    <div className="control-panel">
      {/* Joyride Tour Component */}
      <Joyride
        steps={controlPanelSteps}
        run={runTour}
        continuous
        showProgress
        showSkipButton
        scrollToFirstStep
        scrollOffset={100}
        disableScrolling={false}
        callback={handleJoyrideCallback}
        styles={joyrideStyles}
        locale={{
          back: 'Back',
          close: 'Close',
          last: 'Finish',
          next: 'Next',
          skip: 'Skip Tour',
        }}
      />

      {/* Start Tour Button */}
      <button
        className="tour-button"
        onClick={handleStartTour}
        title="Start Tour Guide"
        aria-label="Start tour guide"
      >
        <HelpCircle size={20} />
        Start Tour
      </button>

      <div className="gov-header">
        <div className="gov-header-content">
          <div className="gov-title-row">
            <div className="gov-logo">
              <img
                src="/logo.png"
                alt="Income Tax Department Logo"
                className="gov-logo-image"
              />
            </div>
            <div className="gov-title-text">
              <h1>Sale Deed AI</h1>
              <p className="gov-subtitle">Income Tax Department - Document Processing System</p>
            </div>
            {/* Notification Bell */}
            <button
              className="notification-bell"
              onClick={() => setShowNotificationCenter(true)}
              title="Notifications"
              aria-label="Notifications"
            >
              <Bell size={24} />
              {unreadCount > 0 && (
                <span className="notification-badge">{unreadCount}</span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="panel-section" role="region" aria-label="PDF Upload Section">
        <h3>
          <Upload size={20} aria-hidden="true" />
          PDF Upload
        </h3>
        <div
          className="upload-area"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileSelect}
            className="file-input"
          />
          <label htmlFor="file-input" className="file-label">
            <FileText size={48} />
            <span>Click to select PDF files or drag and drop</span>
            <span className="file-hint">Multiple files supported</span>
          </label>

          {selectedFiles.length > 0 && (
            <div className="selected-files">
              <h4>Selected Files ({selectedFiles.length}):</h4>
              <ul>
                {selectedFiles.map((file, index) => (
                  <li key={index}>
                    {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={handleUploadClick}
            disabled={loading || selectedFiles.length === 0}
            aria-label="Upload selected PDF files"
          >
            {loading ? <Loader className="spin" size={20} aria-hidden="true" /> : <Upload size={20} aria-hidden="true" />}
            Upload PDFs
          </button>
        </div>

        {uploadStatus && uploadStatus.success && (
          <div className="alert alert-success">
            <CheckCircle size={20} />
            <span>{uploadStatus.message || `Uploaded ${uploadStatus.uploaded_count} files successfully`}</span>
          </div>
        )}

        {/* Display Current Batch ID */}
        {currentBatchId && (
          <div className="alert alert-info">
            <Package size={20} />
            <div className="batch-info-container">
              <strong>Current Batch ID:</strong>
              <code className="batch-id-display">{currentBatchId}</code>
            </div>
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Recent Batches Section */}
        {recentBatches.length > 0 && (
          <div className="recent-batches-section">
            <div className="batches-header">
              <h4>
                <Package size={18} />
                Recent Batches {!showAllBatches && `(Last 5)`}
              </h4>
              {recentBatches.length > 5 && (
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => setShowAllBatches(!showAllBatches)}
                >
                  {showAllBatches ? 'Show Less' : 'View More'}
                </button>
              )}
            </div>

            {showAllBatches && (
              <div className="batch-search-box">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search batches..."
                  value={batchSearchTerm}
                  onChange={(e) => setBatchSearchTerm(e.target.value)}
                />
              </div>
            )}

            <div className={`batches-list ${showAllBatches ? 'expanded' : ''}`}>
              {(() => {
                let filteredBatches = recentBatches;

                // Apply search filter if in expanded mode
                if (showAllBatches && batchSearchTerm) {
                  const searchLower = batchSearchTerm.toLowerCase();
                  filteredBatches = recentBatches.filter(batch =>
                    (batch.batch_name || batch.batch_id).toLowerCase().includes(searchLower) ||
                    batch.batch_id.toLowerCase().includes(searchLower) ||
                    batch.status.toLowerCase().includes(searchLower)
                  );
                }

                // Limit to 5 if not expanded
                const displayBatches = showAllBatches ? filteredBatches : filteredBatches.slice(0, 5);

                return displayBatches.map((batch) => (
                  <div key={batch.batch_id} className="batch-item">
                    <div className="batch-item-header">
                      <div className="batch-name-container">
                        <strong className="batch-name">{batch.batch_name || batch.batch_id}</strong>
                        <span className="batch-status-badge" data-status={batch.status}>
                          {batch.status}
                        </span>
                      </div>
                      <span className="batch-count">{batch.total_count} docs</span>
                    </div>
                    <div className="batch-item-footer">
                      <span className="batch-date">
                        {formatDateIST(batch.created_at)}
                      </span>
                    </div>
                  </div>
                ));
              })()}
            </div>
          </div>
        )}
      </div>

      {/* PDF Processing Section */}
      <div className="panel-section" role="region" aria-label="PDF Processing Section">
        <h3>
          <Play size={20} aria-hidden="true" />
          PDF Processing (OCR + LLM)
        </h3>

        {/* Worker Count Controls */}
        <div className="worker-controls-pipeline">
          <div className="worker-control-row">
            <label className="worker-label">OCR Workers (CPU):</label>
            <div className="worker-buttons">
              <button
                className="btn btn-sm btn-secondary"
                onClick={decreaseOcrWorkers}
                disabled={loading || isPdfProcessingActive || ocrWorkers <= 1}
                title="Decrease OCR workers"
              >
                -
              </button>
              <span className="worker-count">{ocrWorkers}</span>
              <button
                className="btn btn-sm btn-secondary"
                onClick={increaseOcrWorkers}
                disabled={loading || isPdfProcessingActive || ocrWorkers >= 20}
                title="Increase OCR workers"
              >
                +
              </button>
            </div>
          </div>

          <div className="worker-control-row">
            <label className="worker-label">LLM Workers (I/O):</label>
            <div className="worker-buttons">
              <button
                className="btn btn-sm btn-secondary"
                onClick={decreaseLlmWorkers}
                disabled={loading || isPdfProcessingActive || llmWorkers <= 1}
                title="Decrease LLM workers"
              >
                -
              </button>
              <span className="worker-count">{llmWorkers}</span>
              <button
                className="btn btn-sm btn-secondary"
                onClick={increaseLlmWorkers}
                disabled={loading || isPdfProcessingActive || llmWorkers >= 20}
                title="Increase LLM workers"
              >
                +
              </button>
            </div>
          </div>
          <span className="worker-hint">(Max: 20 each)</span>
        </div>

        {/* Advanced OCR Settings */}
        <div className="advanced-settings">
          <h4 className="settings-header">Advanced OCR Settings</h4>

          <div className="worker-control-row">
            <label className="worker-label">Stage-2 Queue Size:</label>
            <div className="worker-buttons">
              <button
                className="btn btn-sm btn-secondary"
                onClick={decreaseQueueSize}
                disabled={loading || isPdfProcessingActive || stage2QueueSize <= 1}
                title="Decrease queue size"
              >
                -
              </button>
              <span className="worker-count">{stage2QueueSize}</span>
              <button
                className="btn btn-sm btn-secondary"
                onClick={increaseQueueSize}
                disabled={loading || isPdfProcessingActive || stage2QueueSize >= 10}
                title="Increase queue size"
              >
                +
              </button>
            </div>
            <span className="setting-hint">(Prevents memory overflow)</span>
          </div>

          <div className="worker-control-row">
            <label className="worker-label">
              <input
                type="checkbox"
                checked={enableOcrMultiprocessing}
                onChange={(e) => setEnableOcrMultiprocessing(e.target.checked)}
                disabled={loading || isPdfProcessingActive}
                className="checkbox-input"
              />
              Enable OCR Multiprocessing
            </label>
            <span className="setting-hint">(Faster for large PDFs, higher CPU/memory)</span>
          </div>

          {enableOcrMultiprocessing && (
            <div className="worker-control-row indent">
              <label className="worker-label">OCR Page Workers:</label>
              <div className="worker-buttons">
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={decreaseOcrPageWorkers}
                  disabled={loading || isPdfProcessingActive || ocrPageWorkers <= 1}
                  title="Decrease OCR page workers"
                >
                  -
                </button>
                <span className="worker-count">{ocrPageWorkers}</span>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={increaseOcrPageWorkers}
                  disabled={loading || isPdfProcessingActive || ocrPageWorkers >= 8}
                  title="Increase OCR page workers"
                >
                  +
                </button>
              </div>
              <span className="setting-hint">(2-4 recommended)</span>
            </div>
          )}

          <div className="worker-control-row">
            <label className="worker-label">
              <input
                type="checkbox"
                checked={useEmbeddedOcr}
                onChange={(e) => handleToggleEmbeddedOcr(e.target.checked)}
                disabled={loading || isPdfProcessingActive}
                className="checkbox-input"
              />
              Use Embedded OCR (PyMuPDF)
            </label>
            <span className="setting-hint">(Read embedded text instead of Tesseract OCR)</span>
          </div>
        </div>

        <div className="control-buttons">
          <button
            className="btn btn-success"
            onClick={handleStartProcessing}
            disabled={loading || isPdfProcessingActive}
          >
            <Play size={20} />
            Start Processing
          </button>
          <button
            className="btn btn-danger"
            onClick={handleStopProcessing}
            disabled={loading}
          >
            <Square size={20} />
            Stop Processing
          </button>
          <button
            className="btn btn-warning"
            onClick={handleRerunFailed}
            disabled={loading || isPdfProcessingActive || (folderStats?.failed || 0) === 0}
            title="Rerun failed PDFs"
          >
            <RefreshCw size={20} />
            Rerun Failed ({folderStats?.failed || 0})
          </button>
          <button
            className="btn btn-info"
            onClick={handleDownloadFailed}
            disabled={loading || (folderStats?.failed || 0) === 0}
            title="Download failed PDFs as ZIP"
          >
            <Download size={20} />
            Download Failed
          </button>
          <button
            className="btn btn-primary"
            onClick={handleViewFailedDocuments}
            disabled={loading || (folderStats?.failed || 0) === 0}
            title="View failed documents by batch"
          >
            <Eye size={20} />
            View Failed Details
          </button>
        </div>

        {processingStats && (
          <div className="stats-section">
            <div className="status-badge">
              {processingStats.is_running || isPdfProcessingActive ? (
                <span className="badge running">
                  <Loader className="spin" size={16} />
                  Processing...
                </span>
              ) : (
                <span className="badge idle">Idle</span>
              )}
            </div>

            <ProgressBar
              value={processingStats.processed}
              max={processingStats.total}
              label="Processing Progress"
            />

            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Total</span>
                <span className="stat-value">{processingStats.total}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Processed</span>
                <span className="stat-value success">{processingStats.processed}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Failed</span>
                <span className="stat-value error">{processingStats.failed}</span>
              </div>
              {processingStats.ocr_active !== undefined && (
                <>
                  <div className="stat-card pipeline">
                    <span className="stat-label">OCR Active</span>
                    <span className="stat-value">{processingStats.ocr_active}</span>
                  </div>
                  <div className="stat-card pipeline">
                    <span className="stat-label">In Queue</span>
                    <span className="stat-value">{processingStats.in_queue || 0}</span>
                  </div>
                  <div className="stat-card pipeline">
                    <span className="stat-label">LLM Active</span>
                    <span className="stat-value">{processingStats.llm_active}</span>
                  </div>
                </>
              )}
              {processingStats.ocr_active === undefined && (
                <div className="stat-card">
                  <span className="stat-label">Active Workers</span>
                  <span className="stat-value">{processingStats.active_workers || 0}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Vision Processing Section */}
      <div className="panel-section" role="region" aria-label="Vision Processing Section">
        <h3>
          <Eye size={20} aria-hidden="true" />
          Vision Processing (Registration Fee Extraction)
        </h3>

        <div className="control-buttons">
          <button
            className="btn btn-success"
            onClick={handleStartVision}
            disabled={loading || isVisionProcessingActive}
          >
            <Eye size={20} />
            Start Vision
          </button>
          <button
            className="btn btn-danger"
            onClick={handleStopVision}
            disabled={loading}
          >
            <Square size={20} />
            Stop Vision
          </button>
        </div>

        {visionStats && (
          <div className="stats-section">
            <div className="status-badge">
              {visionStats.is_running || isVisionProcessingActive ? (
                <span className="badge running">
                  <Loader className="spin" size={16} />
                  Processing...
                </span>
              ) : (
                <span className="badge idle">Idle</span>
              )}
            </div>

            <ProgressBar
              value={visionStats.processed}
              max={visionStats.total}
              label="Vision Progress"
            />

            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Total</span>
                <span className="stat-value">{visionStats.total}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Processed</span>
                <span className="stat-value success">{visionStats.processed}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Failed</span>
                <span className="stat-value error">{visionStats.failed}</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Active Workers</span>
                <span className="stat-value">{visionStats.active_workers || 0}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* User Actions Section */}
      <div className="bottom-actions-section three-column">
        {/* Raise Ticket */}
        <div className="panel-section action-section">
          <h3>
            <AlertCircle size={20} />
            Support Ticket
          </h3>
          <p className="section-description">
            Report issues or errors encountered during processing
          </p>
          <button
            className="btn btn-warning"
            onClick={handleOpenTicketModal}
            disabled={loading}
          >
            <AlertCircle size={20} />
            Raise a Ticket
          </button>
        </div>

        {/* User Records */}
        <div className="panel-section management-section">
          <h3>
            <FileText size={20} />
            User Records
          </h3>
          <p className="section-description">
            View all user registration information and upload history
          </p>
          <button
            className="btn btn-info"
            onClick={handleOpenUserRecordsModal}
            disabled={loading}
          >
            <FileText size={20} />
            View User Records
          </button>
        </div>

        {/* Manage Tickets */}
        <div className="panel-section management-section">
          <h3>
            <AlertCircle size={20} />
            Ticket Management
          </h3>
          <p className="section-description">
            Manage and resolve user-reported issues and errors
          </p>
          <button
            className="btn btn-warning"
            onClick={handleOpenTicketsManagementModal}
            disabled={loading}
          >
            <AlertCircle size={20} />
            Manage Tickets
          </button>
        </div>
      </div>

      {/* User Info Modal */}
      {showUserInfoModal && (
        <div className="modal-overlay" onClick={handleUserInfoCancel}>
          <div className="modal-content user-info-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>User Information</h2>
              <p className="modal-subtitle">Please fill in the required information before uploading</p>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="userName">
                  Name / User Name <span className="required">*</span>
                </label>
                <input
                  id="userName"
                  type="text"
                  className="form-input"
                  placeholder="Enter your name"
                  value={userInfo.userName}
                  onChange={(e) => setUserInfo({ ...userInfo, userName: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="numberOfFiles">
                  Number of Files <span className="required">*</span>
                </label>
                <input
                  id="numberOfFiles"
                  type="number"
                  min="1"
                  className="form-input"
                  placeholder="Auto-filled from selected files"
                  value={userInfo.numberOfFiles}
                  readOnly
                  disabled
                  style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed' }}
                />
                <span className="field-hint">Automatically set to {selectedFiles.length} (based on selected files)</span>
              </div>

              <div className="form-group">
                <label htmlFor="fileRegion">
                  File Region / Location <span className="required">*</span>
                </label>
                <input
                  id="fileRegion"
                  type="text"
                  className="form-input"
                  placeholder="e.g., Hebbal, Chintamani, Goa"
                  value={userInfo.fileRegion}
                  onChange={(e) => setUserInfo({ ...userInfo, fileRegion: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="userInfoDate">Date</label>
                <input
                  id="userInfoDate"
                  type="date"
                  className="form-input"
                  value={userInfo.date}
                  disabled
                  readOnly
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={handleUserInfoCancel}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleUserInfoSubmit}
                disabled={loading}
              >
                {loading ? <Loader className="spin" size={20} /> : 'Submit & Upload'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Ticket Modal */}
      {showTicketModal && (
        <div className="modal-overlay" onClick={handleTicketCancel}>
          <div className="modal-content ticket-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Raise a Support Ticket</h2>
              <p className="modal-subtitle">Report an issue or error you encountered</p>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="ticketUserName">
                  Name <span className="required">*</span>
                </label>
                <input
                  id="ticketUserName"
                  type="text"
                  className="form-input"
                  placeholder="Enter your name"
                  value={ticketForm.userName}
                  onChange={(e) => setTicketForm({ ...ticketForm, userName: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="ticketBatch">
                  Batch <span className="required">*</span>
                </label>
                <div className="searchable-select">
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Search or select a batch..."
                    value={ticketBatchSearchTerm || (ticketForm.batchId ? recentBatches.find(b => b.batch_id === ticketForm.batchId)?.batch_name || ticketForm.batchId : '')}
                    onChange={(e) => {
                      setTicketBatchSearchTerm(e.target.value);
                      setTicketForm({ ...ticketForm, batchId: '' });
                    }}
                    onFocus={() => setTicketBatchSearchTerm(ticketForm.batchId ? '' : ticketBatchSearchTerm)}
                    disabled={loading}
                  />
                  {ticketBatchSearchTerm !== null && ticketBatchSearchTerm !== undefined && (
                    <div className="searchable-select-dropdown">
                      {recentBatches
                        .filter(batch =>
                          (batch.batch_name || batch.batch_id).toLowerCase().includes(ticketBatchSearchTerm.toLowerCase())
                        )
                        .slice(0, 10)
                        .map((batch) => (
                          <div
                            key={batch.batch_id}
                            className="searchable-select-option"
                            onClick={() => {
                              setTicketForm({ ...ticketForm, batchId: batch.batch_id });
                              setTicketBatchSearchTerm(null);
                            }}
                          >
                            {batch.batch_name || batch.batch_id}
                          </div>
                        ))}
                      {recentBatches.filter(batch =>
                        (batch.batch_name || batch.batch_id).toLowerCase().includes(ticketBatchSearchTerm.toLowerCase())
                      ).length === 0 && (
                          <div className="searchable-select-empty">No batches found</div>
                        )}
                    </div>
                  )}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="ticketErrorType">
                  Error Type <span className="required">*</span>
                </label>
                <input
                  id="ticketErrorType"
                  type="text"
                  className="form-input"
                  placeholder="e.g., OCR Error, Data Extraction Error, Processing Failure"
                  value={ticketForm.errorType}
                  onChange={(e) => setTicketForm({ ...ticketForm, errorType: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="ticketDescription">
                  Description <span className="required">*</span>
                </label>
                <textarea
                  id="ticketDescription"
                  className="form-textarea"
                  placeholder="Please describe the issue in detail..."
                  rows="5"
                  value={ticketForm.description}
                  onChange={(e) => setTicketForm({ ...ticketForm, description: e.target.value })}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={handleTicketCancel}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                className="btn btn-warning"
                onClick={handleTicketSubmit}
                disabled={loading}
              >
                {loading ? <Loader className="spin" size={20} /> : 'Submit Ticket'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Records Modal */}
      {showUserRecordsModal && (
        <div className="modal-overlay" onClick={handleCloseUserRecordsModal}>
          <div className="modal-content management-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>User Records</h2>
              <p className="modal-subtitle">View all user registration information and upload history</p>
            </div>

            <div className="modal-body">
              <div className="search-box">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search by name, region, or batch..."
                  value={userRecordsSearchTerm}
                  onChange={(e) => setUserRecordsSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>

              <div className="records-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Files</th>
                      <th>Region</th>
                      <th>Date</th>
                      <th>Batch ID</th>
                    </tr>
                  </thead>
                  <tbody>
                    {userRecords
                      .filter(record =>
                        userRecordsSearchTerm === '' ||
                        record.user_name.toLowerCase().includes(userRecordsSearchTerm.toLowerCase()) ||
                        record.file_region.toLowerCase().includes(userRecordsSearchTerm.toLowerCase()) ||
                        (record.batch_id && record.batch_id.toLowerCase().includes(userRecordsSearchTerm.toLowerCase()))
                      )
                      .map((record) => (
                        <tr key={record.id}>
                          <td>{record.id}</td>
                          <td>{record.user_name}</td>
                          <td>{record.number_of_files}</td>
                          <td>{record.file_region}</td>
                          <td>{formatDateIST(record.date)}</td>
                          <td><code className="batch-code">{getBatchName(record.batch_id)}</code></td>
                        </tr>
                      ))}
                  </tbody>
                </table>
                {userRecords.filter(record =>
                  userRecordsSearchTerm === '' ||
                  record.user_name.toLowerCase().includes(userRecordsSearchTerm.toLowerCase()) ||
                  record.file_region.toLowerCase().includes(userRecordsSearchTerm.toLowerCase()) ||
                  (record.batch_id && record.batch_id.toLowerCase().includes(userRecordsSearchTerm.toLowerCase()))
                ).length === 0 && (
                    <div className="empty-state">No records found</div>
                  )}
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={handleCloseUserRecordsModal}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Support Tickets Management Modal */}
      {showTicketsManagementModal && (
        <div className="modal-overlay" onClick={handleCloseTicketsManagementModal}>
          <div className="modal-content management-modal large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Support Tickets Management</h2>
              <p className="modal-subtitle">Manage and resolve user-reported issues</p>
            </div>

            <div className="modal-body">
              <div className="search-box">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search by name, batch, error type..."
                  value={ticketsSearchTerm}
                  onChange={(e) => setTicketsSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>

              <div className="tickets-list">
                {allTickets
                  .filter(ticket =>
                    ticketsSearchTerm === '' ||
                    ticket.user_name.toLowerCase().includes(ticketsSearchTerm.toLowerCase()) ||
                    ticket.error_type.toLowerCase().includes(ticketsSearchTerm.toLowerCase()) ||
                    (ticket.batch_id && ticket.batch_id.toLowerCase().includes(ticketsSearchTerm.toLowerCase()))
                  )
                  .map((ticket) => (
                    <div key={ticket.id} className={`ticket-card status-${ticket.status}`}>
                      <div className="ticket-header">
                        <div className="ticket-info">
                          <h4>#{ticket.id} - {ticket.user_name}</h4>
                          <span className="ticket-date">{formatDateIST(ticket.created_at)}</span>
                        </div>
                        <select
                          className={`ticket-status-select status-${ticket.status}`}
                          value={ticket.status}
                          onChange={(e) => handleUpdateTicketStatus(ticket.id, e.target.value)}
                          disabled={loading}
                        >
                          <option value="open">Open</option>
                          <option value="in_progress">In Progress</option>
                          <option value="resolved">Resolved</option>
                          <option value="closed">Closed</option>
                        </select>
                      </div>
                      <div className="ticket-body">
                        <div className="ticket-meta">
                          <span><strong>Batch:</strong> <code>{getBatchName(ticket.batch_id)}</code></span>
                          <span><strong>Error Type:</strong> {ticket.error_type}</span>
                        </div>
                        <div className="ticket-description">
                          <strong>Description:</strong>
                          <p>{ticket.description}</p>
                        </div>
                        {ticket.resolved_at && (
                          <div className="ticket-resolved">
                            <strong>Resolved At:</strong> {formatDateIST(ticket.resolved_at)}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                {allTickets.filter(ticket =>
                  ticketsSearchTerm === '' ||
                  ticket.user_name.toLowerCase().includes(ticketsSearchTerm.toLowerCase()) ||
                  ticket.error_type.toLowerCase().includes(ticketsSearchTerm.toLowerCase()) ||
                  (ticket.batch_id && ticket.batch_id.toLowerCase().includes(ticketsSearchTerm.toLowerCase()))
                ).length === 0 && (
                    <div className="empty-state">No tickets found</div>
                  )}
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={handleCloseTicketsManagementModal}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Failed Documents Modal */}
      {showFailedModal && (
        <div className="modal-overlay" onClick={() => setShowFailedModal(false)}>
          <div className="modal-content failed-docs-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                <AlertCircle size={24} />
                Failed Documents by Batch
              </h3>
              <button
                className="close-button"
                onClick={() => setShowFailedModal(false)}
              >
                ×
              </button>
            </div>

            {failedDocuments && (
              <>
                <div className="failed-summary">
                  <div className="summary-item">
                    <span className="summary-label">Total Failed Files:</span>
                    <span className="summary-value">{failedDocuments.total_failed_files || 0}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Affected Batches:</span>
                    <span className="summary-value">{failedDocuments.batch_count || 0}</span>
                  </div>
                </div>

                <div className="failed-batches-list">
                  {failedDocuments.batches && failedDocuments.batches.length > 0 ? (
                    failedDocuments.batches.map((batch) => (
                      <div key={batch.batch_id} className="failed-batch-item">
                        <div
                          className="batch-header"
                          onClick={() => toggleBatchExpansion(batch.batch_id)}
                        >
                          <div className="batch-info">
                            <Package size={18} />
                            <span className="batch-name">{batch.batch_name}</span>
                          </div>
                          <div className="batch-stats">
                            <span className="total-docs">{batch.total_processed} total</span>
                            <span className="failed-count">{batch.failed_count} failed</span>
                            <button
                              className="btn btn-sm btn-primary"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRerunFailedBatch(batch.batch_id);
                              }}
                              disabled={loading}
                            >
                              {loading ? <Loader className="spin" size={14} /> : <RefreshCw size={14} />}
                              Retry Batch
                            </button>
                          </div>
                        </div>

                        {expandedBatches.has(batch.batch_id) && (
                          <div className="failed-files-list">
                            {batch.failed_files.map((file, idx) => (
                              <div key={idx} className="failed-file-item">
                                <FileText size={16} />
                                <span className="filename">{file.filename}</span>
                                <span className="doc-id">{file.document_id}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="no-failures">
                      <CheckCircle size={48} />
                      <p>No failed documents found!</p>
                    </div>
                  )}
                </div>
              </>
            )}

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setShowFailedModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notification Components */}
      <NotificationCenter />
      <ToastNotification />
    </div>
  );
};

export default ControlPanel;