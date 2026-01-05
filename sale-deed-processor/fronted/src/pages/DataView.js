import React, { useState, useEffect } from 'react';
import Joyride, { STATUS } from 'react-joyride';
import { Download, RefreshCw, Search, Loader, AlertCircle, Package, HelpCircle } from 'lucide-react';
import api from '../services/api';
import ExcelJS from 'exceljs';
import { dataViewSteps, joyrideStyles } from '../config/tourSteps';
import '../styles/DataView.css';

const DataView = () => {
  // Format number to remove unnecessary decimals
  const formatNumber = (value) => {
    if (value === null || value === undefined || value === '') return '-';

    // If it's already a number, use it directly
    let num;
    if (typeof value === 'number') {
      num = value;
    } else {
      // If it's a string, remove commas, Rs., /-, and other formatting (but keep decimal point)
      const cleanedValue = String(value)
        .replace(/Rs\.?/gi, '')  // Remove Rs or Rs.
        .replace(/[,\/-]/g, '')   // Remove commas, forward slash, hyphen
        .replace(/\s+/g, '')      // Remove spaces
        .trim();
      num = parseFloat(cleanedValue);
    }

    if (isNaN(num)) return '-';

    // Return the number as-is without modifying it
    // If it's a whole number, show without decimals, otherwise keep decimals
    return num % 1 === 0 ? num.toString() : num.toString();
  };

  // Format date to DD/MM/YYYY, HH:MM:SS AM/PM in GMT+5:30 (IST)
  const formatDateIST = (dateString) => {
    if (!dateString) return '-';

    const date = new Date(dateString);

    // Convert to IST (GMT+5:30)
    const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
    const istDate = new Date(date.getTime() + istOffset);

    const day = String(istDate.getUTCDate()).padStart(2, '0');
    const month = String(istDate.getUTCMonth() + 1).padStart(2, '0');
    const year = istDate.getUTCFullYear();

    let hours = istDate.getUTCHours();
    const minutes = String(istDate.getUTCMinutes()).padStart(2, '0');
    const seconds = String(istDate.getUTCSeconds()).padStart(2, '0');

    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12; // Convert to 12-hour format
    const hoursStr = String(hours).padStart(2, '0');

    return `${day}/${month}/${year}, ${hoursStr}:${minutes}:${seconds} ${ampm}`;
  };

  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [downloadOption, setDownloadOption] = useState('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Batch-related states
  const [batches, setBatches] = useState([]);
  const [selectedBatches, setSelectedBatches] = useState([]);
  const [downloadBatchSearchTerm, setDownloadBatchSearchTerm] = useState('');

  // Display mode: 'rowwise' or 'batchwise'
  const [displayMode, setDisplayMode] = useState('rowwise');
  const [selectedBatchFilter, setSelectedBatchFilter] = useState('all');
  const [batchSearchTerm, setBatchSearchTerm] = useState('');
  const [showBatchDropdown, setShowBatchDropdown] = useState(false);

  // Jump to page state
  const [jumpToPageInput, setJumpToPageInput] = useState('');

  // Tour Guide States
  const [runTour, setRunTour] = useState(false);

  const rowsPerPage = 8;

  useEffect(() => {
    fetchDocuments();
    fetchBatches();
  }, []);

  // Close batch dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showBatchDropdown && !event.target.closest('.custom-select-wrapper')) {
        setShowBatchDropdown(false);
        setBatchSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showBatchDropdown]);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDocuments(0, 1000);
      setDocuments(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const fetchBatches = async () => {
    try {
      const batchList = await api.getBatches();
      setBatches(batchList || []);
    } catch (err) {
      console.error('Error fetching batches:', err);
    }
  };

  const handleDownloadCSV = () => {
    // Open modal to select CSV download options
    setShowDownloadModal(true);
  };



  // Transform data for Excel-like display
  const transformDataForDisplay = (docsToTransform) => {
    const rows = [];

    docsToTransform.forEach((doc) => {
      const buyers = doc.buyers || [];
      const sellers = doc.sellers || [];
      const maxPeople = Math.max(buyers.length, sellers.length, 1);

      for (let i = 0; i < maxPeople; i++) {
        const buyer = buyers[i];
        const seller = sellers[i];

        rows.push({
          document_id: doc.document_id,
          batch_id: doc.batch_id,
          index: i,
          transaction_date: doc.transaction_date,
          registration_office: doc.registration_office,
          property: doc.property_details,
          buyer,
          seller,
        });
      }
    });

    return rows;
  };

  // Filter by batch first if in batchwise mode
  const batchFilteredDocs = displayMode === 'batchwise' && selectedBatchFilter !== 'all'
    ? documents.filter(doc => doc.batch_id === selectedBatchFilter)
    : documents;

  const filteredData = transformDataForDisplay(batchFilteredDocs).filter((row) => {
    // Search filter
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      row.document_id?.toLowerCase().includes(search) ||
      row.buyer?.name?.toLowerCase().includes(search) ||
      row.seller?.name?.toLowerCase().includes(search) ||
      row.property?.address?.toLowerCase().includes(search)
    );
  });

  // Pagination logic
  const totalPages = Math.ceil(filteredData.length / rowsPerPage);
  const startIndex = (currentPage - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const paginatedData = filteredData.slice(startIndex, endIndex);

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  };

  const handleJumpToPage = () => {
    const pageNum = parseInt(jumpToPageInput, 10);
    if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages) {
      setCurrentPage(pageNum);
      setJumpToPageInput('');
    }
  };

  const handleJumpToPageKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleJumpToPage();
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

  const handleConfirmDownload = async () => {
    setShowDownloadModal(false);
    setDownloading(true);

    try {
      let blob;
      let filename = 'sale_deeds_export.csv';

      if (downloadOption === 'all') {
        // Download all documents as CSV
        blob = await api.exportToCSV(null, null, null, null, 'all');
        filename = 'whole_data.csv';
      } else if (downloadOption === 'batch') {
        // Get batch names for selected batches
        const selectedBatchNames = batches
          .filter(batch => selectedBatches.includes(batch.batch_id))
          .map(batch => batch.batch_name || batch.batch_id);

        // Download selected batches as CSV
        blob = await api.exportToCSV(
          selectedBatches,
          selectedBatchNames,
          null,
          null,
          'batch'
        );

        // Set filename based on batch selection
        filename = selectedBatchNames.length === 1
          ? `${selectedBatchNames[0]}.csv`
          : `multiple_batches_${selectedBatchNames.length}.csv`;
      } else if (downloadOption === 'dateRange') {
        // Download by date range as CSV
        blob = await api.exportToCSV(
          null,
          null,
          startDate,
          endDate,
          'dateRange'
        );

        // Set filename based on date range
        if (startDate && endDate) {
          filename = `${startDate}_to_${endDate}.csv`;
        } else if (startDate) {
          filename = `from_${startDate}.csv`;
        } else if (endDate) {
          filename = `to_${endDate}.csv`;
        }
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to download CSV file');
    } finally {
      setDownloading(false);
    }
  };

  const handleBatchSelection = (batchId, isChecked) => {
    if (isChecked) {
      setSelectedBatches([...selectedBatches, batchId]);
    } else {
      setSelectedBatches(selectedBatches.filter(id => id !== batchId));
    }
  };

  const handleSelectAllBatches = () => {
    if (selectedBatches.length === batches.length) {
      // Deselect all
      setSelectedBatches([]);
    } else {
      // Select all
      setSelectedBatches(batches.map(b => b.batch_id));
    }
  };

  // Group rows by document_id for rowspan rendering (using paginated data)
  const groupedData = [];
  let currentDocId = null;
  let rowSpanCount = 0;

  paginatedData.forEach((row, idx) => {
    if (row.document_id !== currentDocId) {
      if (currentDocId !== null) {
        // Update the rowspan for previous group
        const firstIdx = groupedData.findIndex(r => r.document_id === currentDocId && r.isFirst);
        if (firstIdx !== -1) {
          groupedData[firstIdx].rowSpan = rowSpanCount;
        }
      }
      currentDocId = row.document_id;
      rowSpanCount = 1;
      groupedData.push({ ...row, isFirst: true, rowSpan: 1 });
    } else {
      rowSpanCount++;
      groupedData.push({ ...row, isFirst: false });
    }
  });

  // Update last group
  if (currentDocId !== null && groupedData.length > 0) {
    const firstIdx = groupedData.findIndex(r => r.document_id === currentDocId && r.isFirst);
    if (firstIdx !== -1) {
      groupedData[firstIdx].rowSpan = rowSpanCount;
    }
  }

  return (
    <div className="data-view">
      {/* Joyride Tour Component */}
      <Joyride
        steps={dataViewSteps}
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

      <div className="data-header">
        <h2>Data View</h2>

        <div className="data-controls">
          <div className="search-box">
            <Search size={20} />
            <input
              type="text"
              placeholder="Search documents, names, addresses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <button className="btn btn-secondary" onClick={fetchDocuments} disabled={loading}>
            {loading ? <Loader className="spin" size={20} /> : <RefreshCw size={20} />}
            Refresh
          </button>

          <button
            className="btn btn-primary"
            onClick={handleDownloadCSV}
            disabled={downloading || documents.length === 0}
          >
            {downloading ? <Loader className="spin" size={20} /> : <Download size={20} />}
            Download CSV
          </button>
        </div>
      </div>

      {/* Display Mode and Batch Filter Controls */}
      {documents.length > 0 && (
        <div className="view-controls">
          <div className="display-mode-selector">
            <label>Display Mode:</label>
            <div className="radio-group-inline">
              <label>
                <input
                  type="radio"
                  value="rowwise"
                  checked={displayMode === 'rowwise'}
                  onChange={(e) => {
                    setDisplayMode(e.target.value);
                    setSelectedBatchFilter('all');
                    setCurrentPage(1);
                  }}
                />
                All Data (Row-wise)
              </label>
              <label>
                <input
                  type="radio"
                  value="batchwise"
                  checked={displayMode === 'batchwise'}
                  onChange={(e) => {
                    setDisplayMode(e.target.value);
                    setCurrentPage(1);
                  }}
                />
                Batch-wise
              </label>
            </div>
          </div>

          {displayMode === 'batchwise' && (
            <div className="batch-filter-selector">
              <label>Select Batch:</label>
              <div className="custom-select-wrapper">
                <div className="custom-select-input" onClick={() => setShowBatchDropdown(!showBatchDropdown)}>
                  <span>
                    {selectedBatchFilter === 'all'
                      ? 'All Batches'
                      : batches.find(b => b.batch_id === selectedBatchFilter)?.batch_name || selectedBatchFilter
                    }
                  </span>
                  <span className="dropdown-arrow">{showBatchDropdown ? '▲' : '▼'}</span>
                </div>
                {showBatchDropdown && (
                  <div className="custom-select-dropdown">
                    <input
                      type="text"
                      className="batch-search-input"
                      placeholder="Search batches..."
                      value={batchSearchTerm}
                      onChange={(e) => setBatchSearchTerm(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <div className="batch-options">
                      <div
                        className={`batch-option ${selectedBatchFilter === 'all' ? 'selected' : ''}`}
                        onClick={() => {
                          setSelectedBatchFilter('all');
                          setCurrentPage(1);
                          setShowBatchDropdown(false);
                          setBatchSearchTerm('');
                        }}
                      >
                        All Batches
                      </div>
                      {batches
                        .filter(batch =>
                          !batchSearchTerm ||
                          (batch.batch_name || batch.batch_id).toLowerCase().includes(batchSearchTerm.toLowerCase())
                        )
                        .map((batch) => (
                          <div
                            key={batch.batch_id}
                            className={`batch-option ${selectedBatchFilter === batch.batch_id ? 'selected' : ''}`}
                            onClick={() => {
                              setSelectedBatchFilter(batch.batch_id);
                              setCurrentPage(1);
                              setShowBatchDropdown(false);
                              setBatchSearchTerm('');
                            }}
                          >
                            <div className="batch-option-name">{batch.batch_name || batch.batch_id}</div>
                            <div className="batch-option-count">{batch.total_count} docs</div>
                          </div>
                        ))
                      }
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Download Modal */}
      {showDownloadModal && (
        <div className="modal-overlay" onClick={() => setShowDownloadModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Download CSV Options</h3>

            <div className="modal-body">
              <div className="radio-group">
                <label>
                  <input
                    type="radio"
                    value="all"
                    checked={downloadOption === 'all'}
                    onChange={(e) => setDownloadOption(e.target.value)}
                  />
                  Download All Documents
                </label>

                <label>
                  <input
                    type="radio"
                    value="batch"
                    checked={downloadOption === 'batch'}
                    onChange={(e) => setDownloadOption(e.target.value)}
                  />
                  Download by Batch/Session
                </label>

                <label>
                  <input
                    type="radio"
                    value="dateRange"
                    checked={downloadOption === 'dateRange'}
                    onChange={(e) => setDownloadOption(e.target.value)}
                  />
                  Download by Date Range
                </label>
              </div>

              {/* Batch Selection */}
              {downloadOption === 'batch' && (
                <div className="batch-selection">
                  <div className="batch-selection-header">
                    <label>Select Batch(es):</label>
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={handleSelectAllBatches}
                    >
                      {selectedBatches.length === batches.length ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>

                  {/* Search input for batches */}
                  <div className="batch-download-search">
                    <Search size={18} />
                    <input
                      type="text"
                      placeholder="Search batches..."
                      value={downloadBatchSearchTerm}
                      onChange={(e) => setDownloadBatchSearchTerm(e.target.value)}
                    />
                  </div>

                  <div className="batch-list">
                    {batches.length === 0 ? (
                      <p className="no-batches">No batches available</p>
                    ) : (
                      (() => {
                        const filteredBatches = batches.filter(batch =>
                          !downloadBatchSearchTerm ||
                          (batch.batch_name || batch.batch_id).toLowerCase().includes(downloadBatchSearchTerm.toLowerCase()) ||
                          batch.batch_id.toLowerCase().includes(downloadBatchSearchTerm.toLowerCase())
                        );

                        return filteredBatches.length === 0 ? (
                          <p className="no-batches">No batches match your search</p>
                        ) : (
                          filteredBatches.map((batch) => (
                            <label key={batch.batch_id} className="batch-checkbox-item">
                              <input
                                type="checkbox"
                                checked={selectedBatches.includes(batch.batch_id)}
                                onChange={(e) => handleBatchSelection(batch.batch_id, e.target.checked)}
                              />
                              <div className="batch-info">
                                <div className="batch-id-row">
                                  <Package size={16} />
                                  <code className="batch-id-text">{batch.batch_name || batch.batch_id}</code>
                                </div>
                                <div className="batch-meta">
                                  <span className="batch-date">
                                    {formatDateIST(batch.created_at)}
                                  </span>
                                  <span className="batch-count-badge">
                                    {batch.total_count} {batch.total_count === 1 ? 'doc' : 'docs'}
                                  </span>
                                </div>
                              </div>
                            </label>
                          ))
                        );
                      })()
                    )}
                  </div>
                  {selectedBatches.length > 0 && (
                    <div className="batch-selection-summary">
                      Selected: {selectedBatches.length} batch{selectedBatches.length !== 1 ? 'es' : ''}
                    </div>
                  )}
                </div>
              )}

              {/* Date Range */}
              {downloadOption === 'dateRange' && (
                <div className="date-range-inputs">
                  <div className="input-group">
                    <label>Start Date (Created At):</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>
                  <div className="input-group">
                    <label>End Date (Created At):</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowDownloadModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-success"
                onClick={handleConfirmDownload}
                disabled={downloadOption === 'batch' && selectedBatches.length === 0}
              >
                Download
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="loading-container">
          <Loader className="spin" size={48} />
          <p>Loading data...</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="empty-state">
          <p>No documents found. Upload and process PDFs to see data here.</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Document ID</th>
                <th>Transaction Date</th>
                <th>Registration Office</th>
                <th>Schedule B Area (sqft)</th>
                <th>Schedule C Area (sqft)</th>
                <th>Schedule C Address & Name</th>
                <th>Cash Payment</th>
                <th>Property Pincode</th>
                <th>Property State</th>
                <th>Sale Consideration</th>
                <th>Stamp Duty</th>
                <th>Registration Fee</th>
                <th>Guidance Value</th>
                <th>Buyer Name</th>
                <th>Buyer Gender</th>
                <th>Buyer Aadhaar</th>
                <th>Buyer PAN</th>
                <th>Buyer Address</th>
                <th>Buyer Pincode</th>
                <th>Buyer State</th>
                <th>Buyer Phone</th>
                <th>Buyer Email</th>
                <th>Seller Name</th>
                <th>Seller Gender</th>
                <th>Seller Aadhaar</th>
                <th>Seller PAN</th>
                <th>Seller Address</th>
                <th>Seller Pincode</th>
                <th>Seller State</th>
                <th>Seller Phone</th>
                <th>Seller Email</th>
                <th>Seller Share</th>
              </tr>
            </thead>
            <tbody>
              {groupedData.map((row, idx) => (
                <tr key={`${row.document_id}-${idx}`}>
                  {row.isFirst && (
                    <>
                      <td rowSpan={row.rowSpan} className="doc-id-cell">
                        {row.document_id}
                      </td>
                      <td rowSpan={row.rowSpan}>{row.transaction_date || '-'}</td>
                      <td rowSpan={row.rowSpan}>{row.registration_office || '-'}</td>
                      <td rowSpan={row.rowSpan}>{formatNumber(row.property?.schedule_b_area)}</td>
                      <td rowSpan={row.rowSpan}>{formatNumber(row.property?.schedule_c_property_area)}</td>
                      <td rowSpan={row.rowSpan}>
                        {row.property?.schedule_c_property_address || '-'}
                        {row.property?.schedule_c_property_name && row.property?.schedule_c_property_address ? ', ' : ''}
                        {row.property?.schedule_c_property_name || ''}
                      </td>
                      <td rowSpan={row.rowSpan}>{row.property?.paid_in_cash_mode || '-'}</td>
                      <td rowSpan={row.rowSpan}>{row.property?.pincode || '-'}</td>
                      <td rowSpan={row.rowSpan}>{row.property?.state || '-'}</td>
                      <td rowSpan={row.rowSpan}>{formatNumber(row.property?.sale_consideration)}</td>
                      <td rowSpan={row.rowSpan}>{formatNumber(row.property?.stamp_duty_fee)}</td>
                      <td rowSpan={row.rowSpan}>{formatNumber(row.property?.registration_fee)}</td>
                      <td rowSpan={row.rowSpan}>{formatNumber(row.property?.guidance_value)}</td>
                    </>
                  )}
                  <td>{row.buyer?.name || '-'}</td>
                  <td>{row.buyer?.gender || '-'}</td>
                  <td>{row.buyer?.aadhaar_number || '-'}</td>
                  <td>{row.buyer?.pan_card_number || '-'}</td>
                  <td>{row.buyer?.address || '-'}</td>
                  <td>{row.buyer?.pincode || '-'}</td>
                  <td>{row.buyer?.state || '-'}</td>
                  <td>{row.buyer?.phone_number || '-'}</td>
                  <td>{row.buyer?.email || '-'}</td>
                  <td>{row.seller?.name || '-'}</td>
                  <td>{row.seller?.gender || '-'}</td>
                  <td>{row.seller?.aadhaar_number || '-'}</td>
                  <td>{row.seller?.pan_card_number || '-'}</td>
                  <td>{row.seller?.address || '-'}</td>
                  <td>{row.seller?.pincode || '-'}</td>
                  <td>{row.seller?.state || '-'}</td>
                  <td>{row.seller?.phone_number || '-'}</td>
                  <td>{row.seller?.email || '-'}</td>
                  <td>{row.seller?.property_share || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="data-footer">
        <div className="footer-info">
          <p>Total Documents: {documents.length}</p>
          <p>Showing: {startIndex + 1}-{Math.min(endIndex, filteredData.length)} of {filteredData.length} rows</p>
        </div>

        <div className="pagination-controls">
          <button
            className="btn btn-secondary"
            onClick={handlePrevPage}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <span className="page-info">
            Page {currentPage} of {totalPages || 1}
          </span>
          <button
            className="btn btn-secondary"
            onClick={handleNextPage}
            disabled={currentPage === totalPages || totalPages === 0}
          >
            Next
          </button>

          <div className="jump-to-page">
            <input
              type="number"
              min="1"
              max={totalPages || 1}
              placeholder="Page"
              value={jumpToPageInput}
              onChange={(e) => setJumpToPageInput(e.target.value)}
              onKeyDown={handleJumpToPageKeyDown}
              className="page-input"
            />
            <button
              className="btn btn-secondary"
              onClick={handleJumpToPage}
              disabled={totalPages === 0}
            >
              Go
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataView;