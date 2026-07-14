<template>
  <div class="container-fluid bg-light min-vh-100 p-4">
    
    <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
      <h2>Student Dashboard</h2>
      <div>
        <button @click="showProfile = true" class="btn btn-secondary me-2">Edit Profile</button>
        <button @click="triggerExport" class="btn btn-outline-primary me-2">Export History (CSV)</button>
        <button @click="logout" class="btn btn-danger">Logout</button>
      </div>
    </div>

    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <div class="row">
      <div class="col-md-7">
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Open Placement Drives</h5>
            <input type="text" v-model="searchQuery" class="form-control form-control-sm w-50" placeholder="Search company or role...">
          </div>
          <div class="card-body p-0">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr><th>Company</th><th>Job Title</th><th>Min CGPA</th><th>Deadline</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="drive in filteredDrives" :key="drive.id">
                  <td><strong>{{ drive.company_name }}</strong></td>
                  <td>{{ drive.title }}</td>
                  <td>{{ drive.cgpa_req }}</td>
                  <td>{{ drive.deadline }}</td>
                  <td><button @click="apply(drive.id)" class="btn btn-sm btn-success">Apply</button></td>
                </tr>
                <tr v-if="filteredDrives.length === 0">
                  <td colspan="5" class="text-center text-muted py-3">No open drives found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-md-5">
        <div class="card shadow-sm">
          <div class="card-header bg-white">
            <h5 class="mb-0">My Applications</h5>
          </div>
          <div class="card-body p-0">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr><th>Company</th><th>Status</th><th>Date</th></tr>
              </thead>
              <tbody>
                <tr v-for="app in myApplications" :key="app.app_id">
                  <td>{{ app.company_name }} <br><small class="text-muted">{{ app.job_title }}</small></td>
                  <td>
                    <span class="badge" :class="{
                      'bg-warning text-dark': app.status === 'Applied', 'bg-info': app.status === 'Shortlisted',
                      'bg-success': app.status === 'Selected', 'bg-danger': app.status === 'Rejected'
                    }">{{ app.status }}</span>
                  </td>
                  <td>{{ app.applied_on }}</td>
                </tr>
                <tr v-if="myApplications.length === 0">
                  <td colspan="3" class="text-center text-muted py-3">You haven't applied to any drives yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showProfile" class="modal-overlay">
      <div class="modal-content shadow">
        <h4 class="mb-3">Edit Profile</h4>
        <form @submit.prevent="updateProfile">
          <div class="mb-2">
            <label>Current CGPA</label>
            <input type="number" step="0.01" class="form-control" v-model="profileData.cgpa" required>
          </div>
          <div class="mb-2">
            <label>Passing Year</label>
            <input type="number" class="form-control" v-model="profileData.passing_year" required>
          </div>
          <div class="mb-3">
            <label>Resume Link (Google Drive, etc.)</label>
            <input type="url" class="form-control" v-model="profileData.resume_url" placeholder="https://...">
          </div>
          <div class="d-flex justify-content-end">
            <button type="button" class="btn btn-secondary me-2" @click="showProfile = false">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const availableDrives = ref([]);
const myApplications = ref([]);
const message = ref('');
const searchQuery = ref('');

// Profile State
const showProfile = ref(false);
const profileData = ref({ cgpa: '', passing_year: '', resume_url: '' });

// Computed Filter
const filteredDrives = computed(() => {
  if (!searchQuery.value) return availableDrives.value;
  return availableDrives.value.filter(drive => 
    drive.company_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    drive.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Fetch Data
const fetchData = async () => {
  try {
    const drivesRes = await api.get('/student/drives/approved');
    availableDrives.value = drivesRes.data;

    const appsRes = await api.get('/student/applications');
    myApplications.value = appsRes.data;

    const profileRes = await api.get('/student/profile');
    profileData.value = profileRes.data;
  } catch (error) {
    if (error.response?.status === 401 || error.response?.status === 403) logout();
  }
};

onMounted(fetchData);

// Apply
const apply = async (driveId) => {
  try {
    const res = await api.post(`/student/apply/${driveId}`);
    message.value = res.data.message;
    fetchData(); 
  } catch (error) { message.value = error.response?.data?.message || 'Failed to apply.'; }
  setTimeout(() => message.value = '', 5000);
};

// Update Profile
const updateProfile = async () => {
  try {
    await api.put('/student/profile', profileData.value);
    message.value = "Profile updated successfully!";
    showProfile.value = false;
    fetchData(); // Refresh so CGPA matches logic
  } catch (error) {
    message.value = "Failed to update profile.";
  }
  setTimeout(() => message.value = '', 5000);
};

// Trigger Export
const triggerExport = async () => {
  try {
    const res = await api.post('/student/export-history');
    message.value = res.data.message;
  } catch (error) { message.value = 'Failed to trigger export.'; }
  setTimeout(() => message.value = '', 5000);
};

// Logout
const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  router.push('/');
};
</script>

<style scoped>
/* Simple CSS for the Profile Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}
.modal-content {
  background: white;
  padding: 25px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}
</style>