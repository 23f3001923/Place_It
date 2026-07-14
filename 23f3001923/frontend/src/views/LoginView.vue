<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100 py-5">
    <div class="card shadow-lg w-100" style="max-width: 550px;">
      <div class="card-header bg-dark border-bottom-0 p-0">
        <ul class="nav nav-tabs nav-justified" id="authTabs" role="tablist">
          <li class="nav-item">
            <button 
              class="nav-link text-uppercase fw-bold py-3 rounded-0" 
              :class="{ active: currentForm === 'login' }"
              @click="switchForm('login')"
            >
              Sign In
            </button>
          </li>
          <li class="nav-item">
            <button 
              class="nav-link text-uppercase fw-bold py-3 rounded-0" 
              :class="{ active: currentForm === 'registerStudent' }"
              @click="switchForm('registerStudent')"
            >
              Student Join
            </button>
          </li>
          <li class="nav-item">
            <button 
              class="nav-link text-uppercase fw-bold py-3 rounded-0" 
              :class="{ active: currentForm === 'registerCompany' }"
              @click="switchForm('registerCompany')"
            >
              Company Join
            </button>
          </li>
        </ul>
      </div>

      <div class="card-body p-4 bg-white">
        <div v-if="alertMessage" :class="['alert', alertClass, 'alert-dismissible', 'fade', 'show']" role="alert">
          {{ alertMessage }}
          <button type="button" class="btn-close" @click="alertMessage = ''"></button>
        </div>

        <form v-if="currentForm === 'login'" @submit.prevent="handleLogin">
          <h3 class="text-center mb-4 fw-normal text-secondary">Portal Access</h3>
          <div class="mb-3">
            <label class="form-label fw-semibold">Email Address</label>
            <input type="email" class="form-control" v-model="loginForm.email" required placeholder="name@institute.edu">
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold">Password</label>
            <input type="password" class="form-control" v-model="loginForm.password" required placeholder="••••••••">
          </div>
          <button type="submit" class="btn btn-dark w-100 py-2 fs-5" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
            Authenticate
          </button>
        </form>

        <form v-if="currentForm === 'registerStudent'" @submit.prevent="handleRegisterStudent">
          <h3 class="text-center mb-4 fw-normal text-secondary">Student Self-Registration</h3>
          <div class="row g-3">
            <div class="col-md-12">
              <label class="form-label fw-semibold">Full Name</label>
              <input type="text" class="form-control" v-model="studentForm.full_name" required placeholder="John Doe">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Email Address</label>
              <input type="email" class="form-control" v-model="studentForm.email" required placeholder="john@student.com">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Password</label>
              <input type="password" class="form-control" v-model="studentForm.password" required placeholder="••••••••">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Contact Number</label>
              <input type="text" class="form-control" v-model="studentForm.contact_number" required placeholder="+91...">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Academic Branch</label>
              <select class="form-select" v-model="studentForm.branch" required>
                <option value="" disabled selected>Select Branch</option>
                <option value="CSE">Computer Science</option>
                <option value="ECE">Electronics</option>
                <option value="MECH">Mechanical</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Current CGPA</label>
              <input type="number" step="0.01" min="0" max="10" class="form-control" v-model="studentForm.cgpa" required placeholder="e.g. 8.50">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Graduation Year</label>
              <input type="number" class="form-control" v-model="studentForm.graduation_year" required placeholder="2026">
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">Core Skills</label>
              <textarea class="form-control" rows="2" v-model="studentForm.skills" placeholder="Python, JavaScript, VueJS"></textarea>
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2 mt-4 fs-5" :disabled="isLoading">
            Register Account
          </button>
        </form>

        <form v-if="currentForm === 'registerCompany'" @submit.prevent="handleRegisterCompany">
          <h3 class="text-center mb-4 fw-normal text-secondary">Employer Partnership Registration</h3>
          <div class="row g-3">
            <div class="col-md-12">
              <label class="form-label fw-semibold">Company Name</label>
              <input type="text" class="form-control" v-model="companyForm.company_name" required placeholder="Google Inc.">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Corporate Identity Email</label>
              <input type="email" class="form-control" v-model="companyForm.email" required placeholder="hr@company.com">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Password</label>
              <input type="password" class="form-control" v-model="companyForm.password" required placeholder="••••••••">
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">HR Contact Number</label>
              <input type="text" class="form-control" v-model="companyForm.hr_contact" required>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Corporate Website</label>
              <input type="url" class="form-control" v-model="companyForm.website" required>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Industry Sector</label>
              <input type="text" class="form-control" v-model="companyForm.industry" required>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">HQ Location</label>
              <input type="text" class="form-control" v-model="companyForm.location" required>
            </div>
          </div>
          <button type="submit" class="btn btn-success w-100 py-2 mt-4 fs-5" :disabled="isLoading">
            Submit Registration Profile
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginView',
  data() {
    return {
      currentForm: 'login',
      isLoading: false,
      alertMessage: '',
      alertClass: 'alert-danger',
      loginForm: { email: '', password: '' },
      studentForm: {
        email: '', password: '', full_name: '', contact_number: '',
        branch: '', cgpa: '', graduation_year: 2026, skills: ''
      },
      companyForm: {
        email: '', password: '', company_name: '', hr_contact: '',
        website: '', industry: '', location: ''
      }
    }
  },
  methods: {
    switchForm(formName) {
      this.currentForm = formName;
      this.alertMessage = '';
    },
    showAlert(message, type = 'danger') {
      this.alertMessage = message;
      this.alertClass = type === 'danger' ? 'alert-danger' : 'alert-success';
      this.isLoading = false;
    },
    async handleLogin() {
      this.isLoading = true;
      try {
        const response = await axios.post('/api/auth/login', this.loginForm);
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user_role', response.data.role);
        if (response.data.role === 'Admin') this.$router.push('/admin/dashboard');
        else if (response.data.role === 'Company') this.$router.push('/company/dashboard');
        else if (response.data.role === 'Student') this.$router.push('/student/dashboard');
      } catch (error) {
        this.showAlert(error.response?.data?.message || 'Login failed.', 'danger');
      }
    },
    async handleRegisterStudent() {
      this.isLoading = true;
      try {
        await axios.post('/api/auth/register/student', this.studentForm);
        this.showAlert('Registration successful!', 'success');
        this.switchForm('login');
      } catch (error) {
        this.showAlert(error.response?.data?.message || 'Registration failed.', 'danger');
      }
    },
    async handleRegisterCompany() {
      this.isLoading = true;
      try {
        await axios.post('/api/auth/register/company', this.companyForm);
        this.showAlert('Submitted for admin approval.', 'success');
        this.switchForm('login');
      } catch (error) {
        this.showAlert(error.response?.data?.message || 'Submission failed.', 'danger');
      }
    }
  }
}
</script>

<style scoped>
.nav-tabs .nav-link { color: #a0aec0; background-color: #2d3748; border: none; }
.nav-tabs .nav-link.active { color: #fff !important; background-color: #fff !important; border-bottom: 3px solid #3b82f6 !important; }
.nav-tabs .nav-link:hover:not(.active) { color: #fff; background-color: #4a5568; }
.card { border: none; overflow: hidden; }
</style>