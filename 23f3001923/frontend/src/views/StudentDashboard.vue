<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4 bg-white p-3 rounded shadow-sm">
      <div>
        <h2 class="h4 mb-1 fw-bold text-dark">Welcome, {{ profile.full_name || 'Student' }}</h2>
        <p class="mb-0 text-muted small">Manage your profile, discover opportunities, and track your placements.</p>
      </div>
      <div>
        <button class="btn btn-outline-success btn-sm me-2" @click="triggerCSVExport" :disabled="isExporting">
          <i class="bi bi-file-earmark-spreadsheet me-1"></i>
          {{ isExporting ? 'Exporting...' : 'Export History (CSV)' }}
        </button>
      </div>
    </div>

    <div v-if="operationMessage" class="alert alert-info alert-dismissible fade show shadow-sm mb-4" role="alert">
      {{ operationMessage }}
      <button type="button" class="btn-close" @click="operationMessage = ''"></button>
    </div>

    <ul class="nav nav-tabs mb-4" id="studentTabs" role="tablist">
      <li class="nav-item">
        <button class="nav-link active fw-semibold" :class="{ 'active': activeTab === 'jobs' }" @click="switchTab('jobs')">Job Board & Drives</button>
      </li>
      <li class="nav-item">
        <button class="nav-link fw-semibold" :class="{ 'active': activeTab === 'applications' }" @click="switchTab('applications')">My Applications</button>
      </li>
      <li class="nav-item">
        <button class="nav-link fw-semibold" :class="{ 'active': activeTab === 'profile' }" @click="switchTab('profile')">Profile Settings</button>
      </li>
    </ul>

    <div class="tab-content">
      
      <div v-if="activeTab === 'jobs'" class="tab-pane fade show active">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body bg-light p-3 border-bottom">
            <div class="row g-2">
              <div class="col-md-5">
                <input type="text" class="form-control" placeholder="Search by Company Name..." v-model="filters.company" @input="fetchDrives">
              </div>
              <div class="col-md-5">
                <input type="text" class="form-control" placeholder="Search by Job Position..." v-model="filters.position" @input="fetchDrives">
              </div>
              <div class="col-md-2">
                <button class="btn btn-dark w-100" @click="fetchDrives">Search</button>
              </div>
            </div>
          </div>
          
          <div class="card-body p-0 table-responsive" style="max-height: 550px;">
            <table class="table table-hover align-middle m-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-4">Company & Role</th>
                  <th>Salary (LPA)</th>
                  <th>Deadline</th>
                  <th>Eligibility</th>
                  <th class="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in availableDrives" :key="drive.drive_id">
                  <td class="ps-4">
                    <h6 class="mb-1 fw-bold">{{ drive.job_title }}</h6>
                    <small class="text-muted">{{ drive.company_name }}</small>
                  </td>
                  <td class="fw-semibold text-success">₹{{ drive.salary }}</td>
                  <td>{{ new Date(drive.deadline).toLocaleDateString() }}</td>
                  <td>
                    <span v-if="drive.is_eligible" class="badge bg-success">Eligible</span>
                    <span v-else class="badge bg-danger">Not Eligible</span>
                  </td>
                  <td class="text-center">
                    <button v-if="drive.already_applied" class="btn btn-sm btn-secondary" disabled>Applied</button>
                    <button v-else-if="!drive.is_eligible" class="btn btn-sm btn-outline-danger" disabled>Restricted</button>
                    <button v-else class="btn btn-sm btn-primary px-3" @click="applyToDrive(drive.drive_id)">Apply Now</button>
                  </td>
                </tr>
                <tr v-if="availableDrives.length === 0">
                  <td colspan="5" class="text-center py-5 text-muted">No placement drives found matching your criteria.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'applications'" class="tab-pane fade show active">
        <div class="card shadow-sm border-0">
          <div class="card-body p-0 table-responsive" style="max-height: 600px;">
            <table class="table table-hover align-middle m-0 text-center">
              <thead class="table-dark">
                <tr>
                  <th>Date Applied</th>
                  <th>Company</th>
                  <th>Job Position</th>
                  <th>Current Status</th>
                  <th>Feedback / Interview Schedule</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applicationHistory" :key="app.application_id">
                  <td>{{ new Date(app.application_date).toLocaleDateString() }}</td>
                  <td class="fw-semibold">{{ app.company_name }}</td>
                  <td>{{ app.job_title }}</td>
                  <td>
                    <span :class="['badge', app.status === 'Selected' ? 'bg-success' : app.status === 'Shortlisted' ? 'bg-info text-dark' : app.status === 'Rejected' ? 'bg-danger' : 'bg-primary']">
                      {{ app.status }}
                    </span>
                  </td>
                  <td class="text-start">
                    <small class="text-muted" v-if="app.feedback">{{ app.feedback }}</small>
                    <small class="text-muted fst-italic" v-else>Awaiting updates from employer.</small>
                  </td>
                </tr>
                <tr v-if="applicationHistory.length === 0">
                  <td colspan="5" class="text-center py-5 text-muted">You have not applied to any placement drives yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'profile'" class="tab-pane fade show active">
        <div class="card shadow-sm border-0 mx-auto" style="max-width: 800px;">
          <div class="card-header bg-dark text-white py-3">
            <h5 class="card-title mb-0 fw-normal">Update Academic & Contact Profile</h5>
          </div>
          <div class="card-body p-4 bg-white">
            <form @submit.prevent="updateProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-semibold">Full Name</label>
                  <input type="text" class="form-control" v-model="profile.full_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold">Contact Number</label>
                  <input type="text" class="form-control" v-model="profile.contact_number" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold text-muted">Branch (Read Only)</label>
                  <input type="text" class="form-control bg-light" :value="profile.branch" disabled>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold text-muted">CGPA (Read Only)</label>
                  <input type="text" class="form-control bg-light" :value="profile.cgpa" disabled>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold text-muted">Batch (Read Only)</label>
                  <input type="text" class="form-control bg-light" :value="profile.graduation_year" disabled>
                </div>
                <div class="col-md-12">
                  <label class="form-label fw-semibold">Core Skills & Competencies</label>
                  <textarea class="form-control" rows="3" v-model="profile.skills" placeholder="List your technical and soft skills..."></textarea>
                </div>
                <div class="col-md-12">
                  <label class="form-label fw-semibold">Resume Link / Path</label>
                  <input type="text" class="form-control" v-model="profile.resume_path" placeholder="URL to LinkedIn or Drive Resume">
                </div>
              </div>
              <button type="submit" class="btn btn-primary mt-4 w-100 py-2">Save Changes</button>
            </form>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StudentDashboard',
  data() {
    return {
      activeTab: 'jobs', // 'jobs', 'applications', 'profile'
      operationMessage: '',
      isExporting: false,
      
      profile: {},
      availableDrives: [],
      applicationHistory: [],
      
      filters: {
        company: '',
        position: ''
      }
    }
  },
  mounted() {
    this.fetchProfile();
    this.fetchDrives();
    this.fetchHistory();
  },
  methods: {
    // SECURITY FIX: Reusable Auth Header Function
    getAuthHeaders() {
      const token = localStorage.getItem('token');
      return { headers: { Authorization: `Bearer ${token}` } };
    },

    switchTab(tabName) {
      this.activeTab = tabName;
      this.operationMessage = '';
    },
    
    // --- API Interactions ---
    async fetchProfile() {
      try {
        const res = await axios.get('/api/student/profile', this.getAuthHeaders());
        this.profile = res.data;
      } catch (error) {
        console.error("Profile fetch error", error);
      }
    },
    async updateProfile() {
      try {
        const res = await axios.put('/api/student/profile', this.profile, this.getAuthHeaders());
        this.operationMessage = res.data.message;
      } catch (error) {
        this.operationMessage = 'Failed to update profile information.';
      }
    },
    async fetchDrives() {
      try {
        const res = await axios.get('/api/student/drives', {
          params: { company: this.filters.company, position: this.filters.position },
          ...this.getAuthHeaders() // Spread the headers into the config object
        });
        this.availableDrives = res.data;
      } catch (error) {
        console.error("Job drives fetch error", error);
      }
    },
    async fetchHistory() {
      try {
        const res = await axios.get('/api/student/applications', this.getAuthHeaders());
        this.applicationHistory = res.data;
      } catch (error) {
        console.error("Application history fetch error", error);
      }
    },
    async applyToDrive(driveId) {
      if (!confirm("Are you sure you want to apply for this position?")) return;
      try {
        // Pass an empty object {} for the data payload so headers are read correctly
        const res = await axios.post(`/api/student/drives/${driveId}/apply`, {}, this.getAuthHeaders());
        this.operationMessage = res.data.message;
        // Refresh grids to reflect the new application state
        this.fetchDrives();
        this.fetchHistory();
      } catch (error) {
        this.operationMessage = error.response?.data?.message || 'Application submission failed.';
      }
    },
    async triggerCSVExport() {
      this.isExporting = true;
      try {
        // Pass an empty object {} for the data payload
        const res = await axios.post('/api/student/export-applications', {}, this.getAuthHeaders());
        this.operationMessage = res.data.message;
      } catch (error) {
        this.operationMessage = 'Failed to trigger background export task.';
      } finally {
        this.isExporting = false;
      }
    }
  }
}
</script>

<style scoped>
.nav-tabs .nav-link {
  color: #6c757d;
  border-bottom: 2px solid transparent;
}
.nav-tabs .nav-link.active {
  color: #000;
  background-color: transparent;
  border-color: transparent;
  border-bottom: 2px solid #0d6efd;
}
.nav-tabs .nav-link:hover {
  border-color: transparent;
  border-bottom: 2px solid #adb5bd;
}
</style>