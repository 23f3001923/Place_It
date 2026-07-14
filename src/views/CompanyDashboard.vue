<template>
  <div class="container-fluid bg-light min-vh-100 p-4">
    <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
      <h2>Company Dashboard</h2>
      <button @click="logout" class="btn btn-danger">Logout</button>
    </div>

    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <div class="row">
      <div class="col-md-5">
        
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Create Placement Drive</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="createDrive">
              <div class="mb-3"><input type="text" class="form-control" v-model="newDrive.job_title" placeholder="Job Title" required></div>
              <div class="mb-3"><textarea class="form-control" v-model="newDrive.job_description" placeholder="Job Description" required></textarea></div>
              <div class="mb-3"><input type="text" class="form-control" v-model="newDrive.eligibility_branch" placeholder="Allowed Branches (e.g., CSE, IT)" required></div>
              <div class="mb-3"><input type="number" step="0.01" class="form-control" v-model="newDrive.eligibility_cgpa" placeholder="Minimum CGPA" required></div>
              <div class="mb-3">
                <label class="form-label text-muted small">Application Deadline</label>
                <input type="date" class="form-control" v-model="newDrive.application_deadline" required>
              </div>
              <button type="submit" class="btn btn-primary w-100">Submit for Admin Approval</button>
            </form>
          </div>
        </div>

        <div class="card shadow-sm">
          <div class="card-header bg-white">
            <h5 class="mb-0">My Drives</h5>
          </div>
          <ul class="list-group list-group-flush">
            <li v-for="drive in myDrives" :key="drive.id" class="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{{ drive.title }}</strong><br>
                <small class="text-muted">Deadline: {{ drive.deadline }} | Applicants: {{ drive.applicants }}</small>
              </div>
              <span class="badge" :class="drive.status === 'Approved' ? 'bg-success' : 'bg-warning text-dark'">
                {{ drive.status }}
              </span>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-md-7">
        <div class="card shadow-sm">
          <div class="card-header bg-white">
            <h5 class="mb-0">Student Applications</h5>
          </div>
          <div class="card-body p-0">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Student Name</th>
                  <th>Drive</th>
                  <th>CGPA / Branch</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.id">
                  <td><strong>{{ app.student_name }}</strong></td>
                  <td>{{ app.drive_title }}</td>
                  <td>{{ app.student_cgpa }} ({{ app.student_branch }})</td>
                  <td>
                    <span class="badge bg-secondary">{{ app.status }}</span>
                  </td>
                  <td>
                    <select class="form-select form-select-sm" @change="updateStatus(app.id, $event.target.value)">
                      <option value="" disabled selected>Change...</option>
                      <option value="Shortlisted">Shortlist</option>
                      <option value="Selected">Select</option>
                      <option value="Rejected">Reject</option>
                    </select>
                  </td>
                </tr>
                <tr v-if="applications.length === 0">
                  <td colspan="5" class="text-center text-muted py-3">No applications received yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const message = ref('');
const myDrives = ref([]);
const applications = ref([]);

const newDrive = ref({
  job_title: '',
  job_description: '',
  eligibility_branch: '',
  eligibility_cgpa: '',
  application_deadline: ''
});

const fetchData = async () => {
  try {
    const drivesRes = await api.get('/company/drives');
    myDrives.value = drivesRes.data;

    const appsRes = await api.get('/company/applications');
    applications.value = appsRes.data;
  } catch (error) {
    console.error("DASHBOARD API ERROR:", error); // Logs to browser console
    
    // Stop the Ghost Bounce! Only logout if it is explicitly a 401 (Missing Token)
    if (error.response?.status === 401) {
      logout();
    } else {
      // Display the exact error message from Flask on the screen
      message.value = `Backend Error ${error.response?.status}: ` + 
                      (error.response?.data?.msg || error.response?.data?.message || "Unknown Error");
    }
  }
};

// Create a new placement drive
const createDrive = async () => {
  try {
    const res = await api.post('/company/drives', newDrive.value);
    message.value = res.data.message;
    newDrive.value = { job_title: '', job_description: '', eligibility_branch: '', eligibility_cgpa: '', application_deadline: '' };
    fetchData(); // Refresh the list
  } catch (error) {
    message.value = error.response?.data?.message || 'Failed to create drive.';
  }
  setTimeout(() => message.value = '', 5000);
};

// Update student application status
const updateStatus = async (appId, newStatus) => {
  if (!newStatus) return;
  try {
    const res = await api.put(`/company/applications/${appId}/status`, { status: newStatus });
    message.value = res.data.message;
    fetchData(); // Refresh the table
  } catch (error) {
    message.value = 'Failed to update status.';
  }
  setTimeout(() => message.value = '', 3000);
};

// Logout Function
const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  router.push('/');
};
</script>