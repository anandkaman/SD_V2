import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Upload APIs
  async uploadPDFs(files) {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    const response = await this.client.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Processing Control APIs
  async startProcessing(ocrWorkers = 5, llmWorkers = 5, stage2QueueSize = null, enableOcrMultiprocessing = null, ocrPageWorkers = null) {
    const payload = {
      ocr_workers: ocrWorkers,
      llm_workers: llmWorkers
    };

    // Add optional settings only if provided
    if (stage2QueueSize !== null) payload.stage2_queue_size = stage2QueueSize;
    if (enableOcrMultiprocessing !== null) payload.enable_ocr_multiprocessing = enableOcrMultiprocessing;
    if (ocrPageWorkers !== null) payload.ocr_page_workers = ocrPageWorkers;

    const response = await this.client.post('/process/start', payload);
    return response.data;
  }

  async stopProcessing() {
    const response = await this.client.post('/process/stop');
    return response.data;
  }

  async toggleEmbeddedOcr(enabled) {
    const response = await this.client.post(`/process/toggle-embedded-ocr?enabled=${enabled}`);
    return response.data;
  }

  async getProcessingStats() {
    const response = await this.client.get('/process/stats');
    return response.data;
  }

  async rerunFailedPDFs() {
    const response = await this.client.post('/process/rerun-failed');
    return response.data;
  }

  async rerunFailedBatch(batchId) {
    const response = await this.client.post(`/process/rerun-failed-batch?batch_id=${batchId}`);
    return response.data;
  }

  async downloadFailedPDFs() {
    const response = await this.client.get('/process/download-failed', {
      responseType: 'blob',
    });
    return response.data;
  }

  async getFailedDocuments() {
    const response = await this.client.get('/process/failed-documents');
    return response.data;
  }

  // Vision Processing APIs
  async startVisionProcessing() {
    const response = await this.client.post('/vision/start');
    return response.data;
  }

  async stopVisionProcessing() {
    const response = await this.client.post('/vision/stop');
    return response.data;
  }

  async getVisionStats() {
    const response = await this.client.get('/vision/stats');
    return response.data;
  }

  // Data Retrieval APIs
  async getDocuments(skip = 0, limit = 100) {
    const response = await this.client.get('/documents', {
      params: { skip, limit },
    });
    return response.data;
  }

  async getDocument(documentId) {
    const response = await this.client.get(`/documents/${documentId}`);
    return response.data;
  }

  async updateDocument(documentId, updateData) {
    const response = await this.client.patch(`/documents/${documentId}`, updateData);
    return response.data;
  }

  async searchDocuments(filters) {
    const response = await this.client.post('/documents/search', null, {
      params: filters
    });
    return response.data;
  }

  // ✅ ADD THIS NEW METHOD
  async getBatches() {
    const response = await this.client.get('/batches');
    return response.data;
  }

  async exportToExcel(startIndex = 0, endIndex = null, batchIds = null, batchNames = null, startDate = null, endDate = null, downloadType = null) {
    const params = { start_index: startIndex };
    if (endIndex !== null) {
      params.end_index = endIndex;
    }
    if (batchIds !== null && batchIds.length > 0) {
      params.batch_ids = batchIds.join(',');
    }
    if (batchNames !== null && batchNames.length > 0) {
      params.batch_names = batchNames.join(',');
    }
    if (startDate !== null) {
      params.start_date = startDate;
    }
    if (endDate !== null) {
      params.end_date = endDate;
    }
    if (downloadType !== null) {
      params.download_type = downloadType;
    }
    const response = await this.client.get('/export/excel', {
      params,
      responseType: 'blob',
    });
    return response.data;
  }

  async exportToCSV(batchIds = null, batchNames = null, startDate = null, endDate = null, downloadType = null) {
    const params = {};
    if (batchIds !== null && batchIds.length > 0) {
      params.batch_ids = batchIds.join(',');
    }
    if (batchNames !== null && batchNames.length > 0) {
      params.batch_names = batchNames.join(',');
    }
    if (startDate !== null) {
      params.start_date = startDate;
    }
    if (endDate !== null) {
      params.end_date = endDate;
    }
    if (downloadType !== null) {
      params.download_type = downloadType;
    }
    const response = await this.client.get('/export/csv', {
      params,
      responseType: 'blob',
    });
    return response.data;
  }

  // System Info APIs
  async getSystemInfo() {
    const response = await this.client.get('/system/info');
    return response.data;
  }

  async getFolderStats() {
    const response = await this.client.get('/system/folders');
    return response.data;
  }

  async getSystemConfig() {
    const response = await this.client.get('/system/config');
    return response.data;
  }

  // User Info APIs
  async createUserInfo(userInfoData) {
    const response = await this.client.post('/user-info', userInfoData);
    return response.data;
  }

  async getAllUserInfo() {
    const response = await this.client.get('/user-info');
    return response.data;
  }

  async updateUserInfoBatch(batchId, userName) {
    const response = await this.client.patch('/user-info/update-batch', {
      batch_id: batchId,
      user_name: userName
    });
    return response.data;
  }

  // Ticket APIs
  async createTicket(ticketData) {
    const response = await this.client.post('/tickets', ticketData);
    return response.data;
  }

  async getAllTickets() {
    const response = await this.client.get('/tickets');
    return response.data;
  }

  async getTicket(ticketId) {
    const response = await this.client.get(`/tickets/${ticketId}`);
    return response.data;
  }

  async updateTicketStatus(ticketId, status) {
    const response = await this.client.patch(`/tickets/${ticketId}/status`, { status });
    return response.data;
  }

  // Notification APIs
  async getNotifications(limit = 50, unreadOnly = false) {
    const response = await this.client.get('/notifications', {
      params: { limit, unread_only: unreadOnly }
    });
    return response.data;
  }

  async getUnreadCount() {
    const response = await this.client.get('/notifications/unread-count');
    return response.data;
  }

  async markNotificationRead(notificationId) {
    const response = await this.client.patch(`/notifications/${notificationId}/read`);
    return response.data;
  }

  async markAllRead() {
    const response = await this.client.patch('/notifications/mark-all-read');
    return response.data;
  }

  async deleteNotification(notificationId) {
    const response = await this.client.delete(`/notifications/${notificationId}`);
    return response.data;
  }

  // Health Check
  async healthCheck() {
    try {
      const response = await axios.get('http://localhost:8000/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new ApiService();