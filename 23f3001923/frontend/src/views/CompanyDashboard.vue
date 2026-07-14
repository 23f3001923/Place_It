<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4 bg-white p-3 rounded shadow-sm">
      <div>
        <h2 class="h4 mb-1 fw-bold text-dark">{{ stats.company_name }}</h2>
        <p class="mb-0 text-muted small">
          Status: <span class="badge bg-success border-0 px-2">{{ stats.approval_status }}</span>
        </p>
      </div>
      <button class="btn btn-dark" data-bs-toggle="collapse" data-bs-target="#createDrivePanel">
        <i class="bi bi-plus-circle me-2"></i>Post New Placement Drive
      </button>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card bg-white shadow-sm border-0 h-100">
          <div class="card-body p-4 border-start border-4 border-primary">
            <h6 class="text-uppercase text-muted fw-semibold small mb-2">Total Posted Drives</h6>
            <h3 class="fw-bold mb-0 text-dark">{{ stats.total_posted_drives }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-white shadow-sm border-0 h-100">
          <div class="card-body p-4 border-start border-4 border-warning">
            <h6 class="text-uppercase text-muted fw-semibold small mb-2">Applications Received</h6>
            <h3 class="fw-bold mb-0 text-dark">{{ stats.total_received_applications }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-white shadow-sm border-0 h-100">
          <div class="card-body p-4 border-start border-4 border-success">
            <h6 class="text-uppercase text-muted fw-semibold small mb-2">Shortlisted Candidates</h6>
            <h3 class="fw-bold mb-0 text-dark">{{ stats.total_shortlisted_candidates }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div v-if="operationMessage" class="alert alert-info alert-dismissible fade show shadow-sm mb-4" role="alert">
      {{ operationMessage }}
      <button type="button" class="btn-close" @click="operationMessage = ''"></button>
    </div>

    <div class="collapse mb-4" id="createDrivePanel">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-dark text-white py-3">
          <h5 class="card-title mb-0 fw-normal">Configure New Recruitment Drive</h5>
        </div>
        <div class="card-body p-4 bg-white">
          <form @submit.prevent="handleCreateDrive">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label fw-semibold">Job Position Title</label>
                <input type="text" class="form-control" v-model="driveForm.job_title" required placeholder="e.g. Senior Software Engineer">
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Salary Package (LPA)</label>
                <input type="number" step="0.1" class="form-control" v-model="driveForm.salary" required placeholder="e.g. 12.5">
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Eligible Target Year</label>
                <input type="number" class="form-control" v-model="driveForm.eligibility_year" required placeholder="2026">
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Minimum Cutoff CGPA</label>
                <input type="number" step="0.01" min="0" max="10" class="form-control" v-model="driveForm.eligibility_cgpa" required placeholder="7.5">
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Application Deadline</label>
                <input type="datetime-local" class="form-control" v-model="driveForm.application_deadline" required>
              </div>
              <div class="col-md-12">
                <label class="form-label fw-semibold">Eligible Branches</label>
                <input type="text" class="form-control" v-model="driveForm.eligibility_branch" placeholder="e.g. CSE, ECE (or type 'All')">
              </div>
              <div class="col-md-12">
                <label class="form-label fw-semibold">Detailed Job Description & Benefits</label>
                <textarea class="form-control" rows="4" v-model="driveForm.job_description" required placeholder="Outline explicit roles, skill specifications, benefits, and pipeline stages..."></textarea>
              </div>
            </div>
            <button type="submit" class="btn btn-primary mt-4 px-4 py-2">Publish Drive</button>
          </form>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-6">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-dark text-white py-3">
            <h5 class="card-title mb-0 fw-normal">Posted Placements Directory</h5>
          </div>
          <div class="card-body p-0 table-responsive" style="max-height: 500px;">
            <table class="table table-hover align-middle m-0 text-center">
              <thead class="table-light">
                <tr>
                  <th>Job Title</th>
                  <th>Salary</th>
                  <th>Status</th>
                  <th>Action Loops</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id" :class="{'table-active': selectedDriveId === drive.id}">
                  <td class="fw-semibold text-start ps-3">{{ drive.job_title }}</td>
                  <td>₹{{ drive.salary }} LPA</td>
                  <td>
                    <span :class="['badge', drive.status === 'Approved' ? 'bg-success' : drive.status === 'Closed' ? 'bg-secondary' : 'bg-warning text-dark']">
                      {{ drive.status === 'Approved' ? 'Active' : drive.status }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-dark" @click="fetchApplicants(drive.id)">Applicants</button>
                      <button v-if="drive.status === 'Approved'" class="btn btn-outline-danger" @click="toggleDriveLifecycle(drive.id, 'Closed')">Close</button>
                      <button v-if="drive.status === 'Closed'" class="btn btn-outline-success" @click="toggleDriveLifecycle(drive.id, 'Approved')">Reopen</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="drives.length === 0">
                  <td colspan="4" class="text-muted py-4">No hiring drives initialized yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-dark text-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0 fw-normal">Application Review Desk</h5>
            <span v-if="selectedDriveId" class="badge bg-light text-dark">Drive #{{ selectedDriveId }}</span>
          </div>
          <div class="card-body bg-white p-3" style="max-height: 500px; overflow-y: auto;">
            <div v-if="applicants.length === 0" class="text-center py-5 text-muted">
              Select an option from the left table to load application histories.
            </div>
            
            <div v-else class="list-group list-group-flush">
              <div v-for="app in applicants" :key="app.application_id" class="list-group-item py-3 px-0 border-bottom">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <div>
                    <h6 class="mb-1 text-dark fw-bold">{{ app.student_name }}</h6>
                    <p class="mb-0 small text-muted">Branch: <strong>{{ app.branch }}</strong> | CGPA: <strong>{{ app.cgpa }}</strong></p>
                    <small class="text-muted d-block mt-1">Skills: {{ app.skills }}</small>
                  </div>
                  <span :class="['badge', app.status === 'Selected' ? 'bg-success' : app.status === 'Shortlisted' ? 'bg-info' : app.status === 'Rejected' ? 'bg-danger' : 'bg-warning text-dark']">
                    {{ app.status }}
                  </span>
                </div>

                <div class="mt-2 bg-light p-2 rounded small text-secondary mb-3" v-if="app.feedback">
                  <strong>Notes/Log:</strong> {{ app.feedback }}
                </div>

                <div class="d-flex gap-2">
                  <button class="btn btn-sm btn-outline-primary" @click="openReviewModal(app, 'Shortlisted')">Shortlist/Interview</button>
                  <button class="btn btn-sm btn-outline-success" @click="openReviewModal(app, 'Selected')">Offer Placement</button>
                  <button class="btn btn-sm btn-outline-danger" @click="openReviewModal(app, 'Rejected')">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeReview" class="modal-overlay d-flex align-items-center justify-content-center">
      <div class="modal-card bg-white rounded p-4 shadow-lg border w-100" style="max-width: 500px;">
        <h5 class="fw-bold mb-3">Update Applicant Status: <span class="text-primary">{{ activeReview.status }}</span></h5>
        <p class="text-muted small">Target Candidate: {{ activeReview.app.student_name }}</p>
        
        <div class="mb-3" v-if="activeReview.status === 'Shortlisted'">
          <label class="form-label small fw-semibold">Interview Schedule (Date & Time)</label>
          <input type="datetime-local" class="form-control form-control-sm" v-model="activeReview.interview_time">
        </div>
        
        <div class="mb-3">
          <label class="form-label small fw-semibold">Feedback / Placement Remarks</label>
          <textarea class="form-control form-control-sm" rows="3" v-model="activeReview.feedback" placeholder="Provide reason or logistics guidance..."></textarea>
        </div>
        
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-sm btn-secondary" @click="activeReview = null">Cancel</button>
          <button class="btn btn-sm btn-dark" @click="submitReview">Save Decision</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CompanyDashboard',
  data() {
    return {
      stats: { company_name: '', approval_status: '', total_posted_drives: 0, total_received_applications: 0, total_shortlisted_candidates: 0 },
      drives: [],
      applicants: [],
      selectedDriveId: null,
      operationMessage: '',
      activeReview: null,
      
      driveForm: {
        job_title: '', job_description: '', eligibility_branch: 'All',
        eligibility_cgpa: '', eligibility_year: '', salary: '', application_deadline: ''
      }
    }
  },
  mounted() {
    this.refreshCompanyWorkspace();
  },
  methods: {
    getAuthHeaders() {
      const token = localStorage.getItem('token');
      return { headers: { Authorization: `Bearer ${token}` } };
    },
    async refreshCompanyWorkspace() {
      try {
        const statsRes = await axios.get('/api/company/dashboard/stats', this.getAuthHeaders());
        this.stats = statsRes.data;
        
        const drivesRes = await axios.get('/api/company/drives', this.getAuthHeaders());
        this.drives = drivesRes.data;
      } catch (error) {
        this.operationMessage = 'Access denied or profile requires system verification approvals.';
      }
    },
    async handleCreateDrive() {
      try {
        const payload = { ...this.driveForm };
        payload.application_deadline = payload.application_deadline.replace(' ', 'T');
        
        const res = await axios.post('/api/company/drives', payload, this.getAuthHeaders());
        this.operationMessage = res.data.message;
        
        this.driveForm = { job_title: '', job_description: '', eligibility_branch: 'All', eligibility_cgpa: '', eligibility_year: '', salary: '', application_deadline: '' };
        this.refreshCompanyWorkspace();
      } catch (error) {
        this.operationMessage = error.response?.data?.message || 'Drive publishing constraint failure.';
      }
    },
    async toggleDriveLifecycle(driveId, status) {
      try {
        const res = await axios.patch(`/api/company/drives/${driveId}/lifecycle`, { status }, this.getAuthHeaders());
        this.operationMessage = res.data.message;
        this.refreshCompanyWorkspace();
      } catch (error) {
        this.operationMessage = error.response?.data?.message || 'Lifecycle management state adjustment restricted.';
      }
    },
    async fetchApplicants(driveId) {
      this.selectedDriveId = driveId;
      try {
        const res = await axios.get(`/api/company/drives/${driveId}/applicants`, this.getAuthHeaders());
        this.applicants = res.data;
      } catch (error) {
        this.operationMessage = 'Failed to load specific applicant directory listings.';
      }
    },
    openReviewModal(applicant, targetedStatus) {
      this.activeReview = {
        app: applicant,
        status: targetedStatus,
        feedback: '',
        interview_time: ''
      };
    },
    async submitReview() {
      if (!this.activeReview) return;
      
      try {
        const payload = {
          status: this.activeReview.status,
          feedback: this.activeReview.feedback
        };
        
        if (this.activeReview.status === 'Shortlisted' && this.activeReview.interview_time) {
          payload.interview_time = new Date(this.activeReview.interview_time).toLocaleString();
        }
        
        const res = await axios.patch(`/api/company/applications/${this.activeReview.app.application_id}/review`, payload, this.getAuthHeaders());
        this.operationMessage = res.data.message;
        
        this.activeReview = null;
        this.fetchApplicants(this.selectedDriveId);
        this.refreshCompanyWorkspace();
      } catch (error) {
        this.operationMessage = 'Failed to submit the application evaluation decision.';
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1050;
}
.modal-card {
  z-index: 1060;
}
.table-active {
  border-left: 4px solid #1e293b !important;
}
</style>