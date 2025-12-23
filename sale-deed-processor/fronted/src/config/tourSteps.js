// Control Panel Tour Steps Configuration
export const controlPanelSteps = [
  {
    target: 'body',
    content: (
      <div>
        <h2>Welcome to SaleDeed AI! 👋</h2>
        <p>Let's take a quick tour to help you understand how to process sale deed documents efficiently.</p>
      </div>
    ),
    placement: 'center',
    disableBeacon: true,
  },
  {
    target: '.upload-area',
    content: (
      <div>
        <h3>Upload PDF Documents</h3>
        <p>Click here or drag & drop your sale deed PDF files. You can upload multiple files at once.</p>
      </div>
    ),
    placement: 'bottom',
  },
  {
    target: '.control-buttons',
    content: (
      <div>
        <h3>Upload & Start Processing</h3>
        <p>After selecting files, you'll be asked to provide user information. Then click "Start Processing" to begin extracting data.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: '.worker-controls-pipeline',
    content: (
      <div>
        <h3>Configure Workers</h3>
        <p>Adjust OCR and LLM workers to optimize processing speed based on your system capabilities.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: '.stats-grid',
    content: (
      <div>
        <h3>Monitor Progress</h3>
        <p>Track the processing status: processed, failed, and remaining documents in real-time.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: '.recent-batches-section',
    content: (
      <div>
        <h3>View Recent Batches</h3>
        <p>All your uploaded batches are listed here. Click on any batch to download processed data.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: '.batch-search-box',
    content: (
      <div>
        <h3>Search Batches</h3>
        <p>Use the search box to quickly find a specific batch by name or ID.</p>
      </div>
    ),
    placement: 'bottom',
  },
  {
    target: '.bottom-actions-section .panel-section:nth-child(1)',
    content: (
      <div>
        <h3>Report Issues</h3>
        <p>Encountered an error? Raise a support ticket to report issues with specific batches.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: '.bottom-actions-section .panel-section:nth-child(2)',
    content: (
      <div>
        <h3>View User Records</h3>
        <p>Access all user registration information and upload history here.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: '.bottom-actions-section .panel-section:nth-child(3)',
    content: (
      <div>
        <h3>Manage Support Tickets</h3>
        <p>Developers and admins can view and resolve user-reported issues here.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: 'body',
    content: (
      <div>
        <h2>You're All Set! 🎉</h2>
        <p>You now know how to use the Control Panel. Upload your documents and start processing!</p>
      </div>
    ),
    placement: 'center',
  },
];

// DataView Tour Steps Configuration
export const dataViewSteps = [
  {
    target: 'body',
    content: (
      <div>
        <h2>Welcome to DataView! 📊</h2>
        <p>Here you can view, search, filter, and export all processed sale deed data.</p>
      </div>
    ),
    placement: 'center',
    disableBeacon: true,
  },
  {
    target: '.data-header',
    content: (
      <div>
        <h3>Data View Controls</h3>
        <p>Use the search box to find specific documents and click Refresh to reload the latest data from the database.</p>
      </div>
    ),
    placement: 'bottom',
  },
  {
    target: '.search-box',
    content: (
      <div>
        <h3>Search Documents</h3>
        <p>Search by document ID, buyer name, seller name, property details, or any other field.</p>
      </div>
    ),
    placement: 'bottom',
  },
  {
    target: '.view-controls',
    content: (
      <div>
        <h3>Display & Filter Options</h3>
        <p>Switch between different view modes: All Documents, or filter by Batch. You can also download data in various formats.</p>
      </div>
    ),
    placement: 'bottom',
  },
  {
    target: '.table-container',
    content: (
      <div>
        <h3>View Extracted Data</h3>
        <p>All extracted information is displayed here: document details, property info, buyer/seller details, and financial data.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: '.data-footer',
    content: (
      <div>
        <h3>Navigate Records</h3>
        <p>Use pagination to navigate through large datasets. Total document count and current range are shown here.</p>
      </div>
    ),
    placement: 'top',
  },
  {
    target: 'body',
    content: (
      <div>
        <h2>You're Ready to Explore! 🎉</h2>
        <p>You can now view, search, filter, and export processed sale deed data efficiently. Click on download buttons to export data in different formats.</p>
      </div>
    ),
    placement: 'center',
  },
];

// Custom Joyride Styles
export const joyrideStyles = {
  options: {
    primaryColor: '#613AF5',
    textColor: '#333',
    backgroundColor: '#fff',
    overlayColor: 'rgba(0, 0, 0, 0.5)',
    arrowColor: '#fff',
    zIndex: 10000,
  },
  tooltip: {
    borderRadius: '8px',
    padding: '20px',
    fontSize: '15px',
  },
  tooltipContainer: {
    textAlign: 'left',
  },
  tooltipTitle: {
    fontSize: '18px',
    fontWeight: '700',
    marginBottom: '8px',
  },
  tooltipContent: {
    padding: '10px 0',
  },
  buttonNext: {
    backgroundColor: '#613AF5',
    borderRadius: '6px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '600',
  },
  buttonBack: {
    color: '#613AF5',
    marginRight: '10px',
    fontSize: '14px',
    fontWeight: '600',
  },
  buttonSkip: {
    color: '#666',
    fontSize: '14px',
    fontWeight: '600',
  },
  buttonClose: {
    position: 'absolute',
    top: '8px',
    right: '8px',
    height: '32px',
    width: '32px',
    padding: '0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    color: '#666',
    fontSize: '24px',
    fontWeight: '300',
    lineHeight: '1',
    transition: 'all 0.2s ease',
  },
  spotlight: {
    borderRadius: '4px',
  },
};
