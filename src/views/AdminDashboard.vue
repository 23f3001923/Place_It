<template>
  <div class="container-fluid bg-light min-vh-100 p-4">
    <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
      <h2>Admin Dashboard</h2>
      <button @click="logout" class="btn btn-danger">Logout</button>
    </div>

    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-primary text-white text-center">
          <div class="card-body">
            <h1 class="display-5 fw-bold">{{ stats.total_students || 0 }}</h1>
            <p class="mb-0">Registered Students</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-success text-white text-center">
          <div class="card-body">
            <h1 class="display-5 fw-bold">{{ stats.total_companies || 0 }}</h1>
            <p class="mb-0">Registered Companies</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-info text-white text-center">
          <div class="card-body">
            <h1 class="display-5 fw-bold">{{ stats.total_drives || 0 }}</h1>
            <p class="mb-0">Placement Drives</p>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Pending Company Approvals</h5>
            <input type="text" v-model="searchCompany" class="form-control form-control-sm w-50" placeholder="Search company...">
          </div>
          <div class="card-body p-0">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr><th>Company Name</th><th>HR Contact</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="company in filteredCompanies" :key="company.id">
                  <td><strong>{{ company.name }}</strong></td>
                  <td>{{ company.hr }}</td>
                  <td>
                    <button @click="updateCompany(company.id, 'Approved')" class="btn btn-sm btn-success me-1">Approve</button>
                    <button @click="updateCompany(company.id, 'Rejected')" class="btn btn-sm btn-danger">Reject</button>
                  </td>
                </tr>
                <tr v-if="filteredCompanies.length === 0">
                  <td colspan="3" class="text-center text-muted py-3">No matching companies found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-md-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Pending Placement Drives</h5>
            <input type="text" v-model="searchDrive" class="form-control form-control-sm w-50" placeholder="Search job title...">
          </div>
          <div class="card-body p-0">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr><th>Company</th><th>Job Title</th><th>Action</th></tr>
              </thead>
              <tbody>
                <tr v-for="drive in filteredDrives" :key="drive.id">
                  <td><strong>{{ drive.company }}</strong></td>
                  <td>{{ drive.title }}</td>
                  <td>
                    <button @click="updateDrive(drive.id, 'Approved')" class="btn btn-sm btn-success me-1">Approve</button>
                    <button @click="updateDrive(drive.id, 'Rejected')" class="btn btn-sm btn-danger">Reject</button>
                  </td>
                </tr>
                <tr v-if="filteredDrives.length === 0">
                  <td colspan="3" class="text-center text-muted py-3">No matching drives found.</td>
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const message = ref('');
const stats = ref({});
const pendingCompanies = ref([]);
const pendingDrives = ref([]);

// Search State
const searchCompany = ref('');
const searchDrive = ref('');

// Computed Filters
const filteredCompanies = computed(() => {
  if (!searchCompany.value) return pendingCompanies.value;
  return pendingCompanies.value.filter(c => c.name.toLowerCase().includes(searchCompany.value.toLowerCase()));
});

const filteredDrives = computed(() => {
  if (!searchDrive.value) return pendingDrives.value;
  return pendingDrives.value.filter(d => d.title.toLowerCase().includes(searchDrive.value.toLowerCase()));
});

const fetchData = async () => {
  try {
    const statsRes = await api.get('/admin/dashboard/stats');
    stats.value = statsRes.data;
    const pendingRes = await api.get('/admin/pending');
    pendingCompanies.value = pendingRes.data.companies;
    pendingDrives.value = pendingRes.data.drives;
  } catch (error) {
    if (error.response?.status === 401) logout();
  }
};

onMounted(fetchData);

const updateCompany = async (companyId, newStatus) => {
  try {
    const res = await api.put(`/admin/company/${companyId}/status`, { status: newStatus });
    message.value = res.data.message;
    fetchData(); 
  } catch (error) { message.value = 'Failed to update status.'; }
  setTimeout(() => message.value = '', 3000);
};

const updateDrive = async (driveId, newStatus) => {
  try {
    const res = await api.put(`/admin/drive/${driveId}/status`, { status: newStatus });
    message.value = res.data.message;
    fetchData(); 
  } catch (error) { message.value = 'Failed to update status.'; }
  setTimeout(() => message.value = '', 3000);
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  router.push('/');
};
</script>