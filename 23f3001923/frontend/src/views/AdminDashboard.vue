<template>
  <div class="container-fluid py-4">
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white shadow-sm border-0 h-100">
          <div class="card-body d-flex flex-column justify-content-between p-4">
            <h6 class="text-uppercase fw-semibold opacity-75 m-0">Total Enrolled Students</h6>
            <h2 class="display-5 fw-bold my-2">{{ stats.total_students }}</h2>
            <small class="opacity-50">Verified Profiles</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white shadow-sm border-0 h-100">
          <div class="card-body d-flex flex-column justify-content-between p-4">
            <h6 class="text-uppercase fw-semibold opacity-75 m-0">Corporate Partners</h6>
            <h2 class="display-5 fw-bold my-2">{{ stats.total_companies }}</h2>
            <small class="opacity-50">Registered Organizations</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-dark shadow-sm border-0 h-100">
          <div class="card-body d-flex flex-column justify-content-between p-4">
            <h6 class="text-uppercase fw-semibold opacity-75 m-0">Placement Drives</h6>
            <h2 class="display-5 fw-bold my-2">{{ stats.total_placement_drives }}</h2>
            <small class="opacity-50">Active & Closed Campaigns</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white shadow-sm border-0 h-100">
          <div class="card-body d-flex flex-column justify-content-between p-4">
            <h6 class="text-uppercase fw-semibold opacity-75 m-0">Applications Processed</h6>
            <h2 class="display-5 fw-bold my-2">{{ stats.total_applications }}</h2>
            <small class="opacity-50">Recruitment Intersections</small>
          </div>
        </div>
      </div>
    </div>

    <div v-if="operationMessage" class="alert alert-dark alert-dismissible fade show shadow-sm mb-4" role="alert">
      {{ operationMessage }}
      <button type="button" class="btn-close" @click="operationMessage = ''"></button>
    </div>

    <div class="row g-4">
      <div class="col-lg-7">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-header bg-dark text-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="card-title m-0 fw-normal">Corporate Directory & Approvals</h5>
            <div class="d-flex gap-2 w-50">
              <input type="text" class="form-control form-control-sm" placeholder="Filter Name..." v-model="filters.companyName" @input="fetchCompanies">
              <input type="text" class="form-control form-control-sm" placeholder="Industry..." v-model="filters.companyIndustry" @input="fetchCompanies">
            </div>
          </div>
          <div class="card-body p-0 table-responsive" style="max-height: 350px;">
            <table class="table table-hover align-middle m-0 text-center">
              <thead class="table-light">
                <tr>
                  <th>Company</th>
                  <th>Industry</th>
                  <th>Location</th>
                  <th>Approval Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="company in companies" :key="company.id">
                  <td class="fw-semibold">{{ company.company_name }}</td>
                  <td>{{ company.industry }}</td>
                  <td>{{ company.location }}</td>
                  <td>
                    <span :class="['badge', company.status === 'Approved' ? 'bg-success' : company.status === 'Blacklisted' ? 'bg-danger' : 'bg-warning text-dark']">
                      {{ company.status }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button v-if="company.status === 'Pending'" class="btn btn-outline-success" @click="updateCompanyStatus(company.id, 'Approved')">Approve</button>
                      <button v-if="company.status === 'Approved'" class="btn btn-outline-warning" @click="updateCompanyStatus(company.id, 'Pending')">Revoke</button>
                      <button class="btn btn-outline-danger" @click="toggleUserActive(company.id, 'Company')">
                        {{ company.status === 'Blacklisted' ? 'Reactivate' : 'Blacklist' }}
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="companies.length === 0">
                  <td colspan="5" class="text-muted py-4">No enterprise entities match your active query.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-header bg-dark text-white py-3">
            <h5 class="card-title m-0 fw-normal">Global Placement Drive Pipeline</h5>
          </div>
          <div class="card-body p-0 table-responsive" style="max-height: 300px;">
            <table class="table table-hover align-middle m-0 text-center">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Job Title</th>
                  <th>Salary (LPA)</th>
                  <th>Deadline State</th>
                  <th>Workflow Status</th>
                  <th>Action Verification</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td>#{{ drive.id }}</td>
                  <td class="fw-semibold">{{ drive.job_title }}</td>
                  <td>₹{{ drive.salary }}</td>
                  <td>{{ (drive.deadline && drive.deadline !== 'N/A') ? new Date(drive.deadline).toLocaleDateString() : 'N/A' }}</td>
                  <td>
                    <span :class="['badge', drive.status === 'Approved' ? 'bg-success' : drive.status === 'Closed' ? 'bg-secondary' : 'bg-warning text-dark']">
                      {{ drive.status === 'Approved' ? 'Active / Approved' : drive.status }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button v-if="drive.status === 'Pending'" class="btn btn-success" @click="updateDriveStatus(drive.id, 'Approved')">Verify & Open</button>
                      <button v-if="drive.status === 'Approved'" class="btn btn-danger" @click="updateDriveStatus(drive.id, 'Closed')">Terminate / Close</button>
                      <span v-else-if="drive.status === 'Closed'" class="text-muted fst-italic">Lifecycle Completed</span>
                    </div>
                  </td>
                </tr>
                <tr v-if="drives.length === 0">
                  <td colspan="6" class="text-muted py-4">No corporate deployment operations found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-lg-5">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-dark text-white py-3">
            <h5 class="card-title m-0 fw-normal">Student Roster Audit Controls</h5>
          </div>
          <div class="card-body p-4 bg-white">
            <div class="row g-2 mb-3">
              <div class="col-md-5">
                <input type="text" class="form-control form-control-sm" placeholder="Search Name..." v-model="filters.studentName">
              </div>
              <div class="col-md-4">
                <input type="text" class="form-control form-control-sm" placeholder="Contact number..." v-model="filters.studentContact">
              </div>
              <div class="col-md-3">
                <button class="btn btn-sm btn-secondary w-100" @click="fetchStudents">Execute Audit</button>
              </div>
            </div>

            <div class="table-responsive" style="max-height: 600px;">
              <ul class="list-group list-group-flush">
                <li v-for="student in students" :key="student.id" class="list-group-item d-flex justify-content-between align-items-center px-0 py-3 border-bottom">
                  <div>
                    <h6 class="mb-1 text-dark fw-semibold">{{ student.full_name }} <small class="text-muted">(ID: {{ student.id }})</small></h6>
                    <p class="mb-0 text-muted small">
                      Branch: <span class="badge bg-light text-dark">{{ student.branch }}</span> | CGPA: <strong>{{ student.cgpa }}</strong> | Batch: {{ student.graduation_year }}
                    </p>
                    <small class="text-muted">Contact: {{ student.contact_number }}</small>
                  </div>
                  <button class="btn btn-sm btn-outline-danger ms-2" @click="toggleUserActive(student.id, 'Student')">
                    Deactivate
                  </button>
                </li>
                <li v-if="students.length === 0" class="text-center py-5 text-muted">
                  Initiate an audit request query parameters to retrieve student profile items.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: { total_students: 0, total_companies: 0, total_placement_drives: 0, total_applications: 0 },
      companies: [],
      drives: [],
      students: [],
      operationMessage: '',
      filters: {
        companyName: '',
        companyIndustry: '',
        studentName: '',
        studentContact: ''
      }
    }
  },
  mounted() {
    this.refreshDashboardCore();
  },
  methods: {
    getAuthHeaders() {
      const token = localStorage.getItem('token');
      return { headers: { Authorization: `Bearer ${token}` } };
    },
    async refreshDashboardCore() {
      try {
        const statsRes = await axios.get('/api/admin/dashboard/stats', this.getAuthHeaders());
        this.stats = statsRes.data;
        
        await this.fetchCompanies();
        await this.fetchDrives();
      } catch (error) {
        this.operationMessage = 'Failed to extract administrative summary details.';
      }
    },
    async fetchCompanies() {
      try {
        const res = await axios.get('/api/admin/search/companies', {
          params: { name: this.filters.companyName, industry: this.filters.companyIndustry },
          ...this.getAuthHeaders()
        });
        this.companies = res.data;
      } catch (error) {
        console.error('Company matrix sync failure:', error);
      }
    },
    async fetchDrives() {
      try {
        const res = await axios.get('/api/admin/drives', this.getAuthHeaders());
        this.drives = res.data;
        
        if (this.operationMessage && this.operationMessage.includes('Drive Pipeline Error')) {
          this.operationMessage = ''; 
        }
      } catch (error) {
        console.error("Admin Drives Fetch Error:", error.response || error);
        const status = error.response ? error.response.status : 'Network Error';
        this.operationMessage = `Drive Pipeline Error: Backend returned ${status}. Check Terminal.`;
        this.drives = [];
      }
    },
    async fetchStudents() {
      try {
        const res = await axios.get('/api/admin/search/students', {
          params: { name: this.filters.studentName, contact: this.filters.studentContact },
          ...this.getAuthHeaders()
        });
        this.students = res.data;
      } catch (error) {
        this.operationMessage = 'Student listing index retrieval error.';
      }
    },
    async updateCompanyStatus(companyId, status) {
      try {
        const res = await axios.patch(`/api/admin/companies/${companyId}/status`, { status }, this.getAuthHeaders());
        this.operationMessage = res.data.message;
        await this.refreshDashboardCore();
      } catch (error) {
        this.operationMessage = 'Unable to mutate target company verification status context.';
      }
    },
    async updateDriveStatus(driveId, status) {
      try {
        const res = await axios.patch(`/api/admin/drives/${driveId}/status`, { status }, this.getAuthHeaders());
        this.operationMessage = res.data.message;
        await this.refreshDashboardCore();
      } catch (error) {
        this.operationMessage = 'Unable to transition structural placement drive workflow lifecycle state.';
      }
    },
    async toggleUserActive(profileId, role) {
      if (!confirm(`Confirm account termination or verification state toggle operations for this ${role}?`)) return;
      try {
        const res = await axios.patch(`/api/admin/users/${profileId}/toggle-active`, { role }, this.getAuthHeaders());
        this.operationMessage = res.data.message;
        await this.refreshDashboardCore();
        if (role === 'Student') await this.fetchStudents();
      } catch (error) {
        this.operationMessage = 'Systemic profile termination failure occurred.';
      }
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 8px;
}
.table-responsive {
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}
</style>