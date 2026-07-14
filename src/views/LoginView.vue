<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-header bg-dark text-white text-center">
            <h4>Placement Portal</h4>
          </div>
          <div class="card-body">
            
            <form @submit.prevent="handleLogin" v-if="viewMode === 'login'">
              <div class="mb-3">
                <label>Email address</label>
                <input type="email" class="form-control" v-model="loginData.email" required>
              </div>
              <div class="mb-3">
                <label>Password</label>
                <input type="password" class="form-control" v-model="loginData.password" required>
              </div>
              <button type="submit" class="btn btn-primary w-100">Login</button>
              <div class="mt-3 text-center d-flex justify-content-around">
                <a href="#" @click.prevent="viewMode = 'studentReg'">Register as Student</a>
                <a href="#" class="text-success" @click.prevent="viewMode = 'companyReg'">Register as Company</a>
              </div>
            </form>

            <form @submit.prevent="handleStudentRegister" v-else-if="viewMode === 'studentReg'">
              <h5 class="text-center mb-3">Student Registration</h5>
              <div class="mb-2"><input type="text" class="form-control" v-model="studentRegData.full_name" placeholder="Full Name" required></div>
              <div class="mb-2"><input type="email" class="form-control" v-model="studentRegData.email" placeholder="Email Address" required></div>
              <div class="mb-2"><input type="password" class="form-control" v-model="studentRegData.password" placeholder="Password" required></div>
              <div class="mb-2"><input type="text" class="form-control" v-model="studentRegData.branch" placeholder="Branch (e.g., CSE)" required></div>
              <div class="mb-2"><input type="number" step="0.01" class="form-control" v-model="studentRegData.cgpa" placeholder="CGPA (e.g., 8.5)" required></div>
              <div class="mb-2"><input type="number" class="form-control" v-model="studentRegData.passing_year" placeholder="Passing Year" required></div>
              <button type="submit" class="btn btn-primary w-100">Register</button>
              <div class="mt-2 text-center"><a href="#" @click.prevent="viewMode = 'login'">Back to Login</a></div>
            </form>

            <form @submit.prevent="handleCompanyRegister" v-else-if="viewMode === 'companyReg'">
              <h5 class="text-center mb-3 text-success">Company Registration</h5>
              <div class="mb-2"><input type="text" class="form-control" v-model="companyRegData.company_name" placeholder="Company Name" required></div>
              <div class="mb-2"><input type="text" class="form-control" v-model="companyRegData.hr_contact" placeholder="HR Contact Name" required></div>
              <div class="mb-2"><input type="text" class="form-control" v-model="companyRegData.website" placeholder="Website URL (Optional)"></div>
              <div class="mb-2"><input type="email" class="form-control" v-model="companyRegData.email" placeholder="Company Email" required></div>
              <div class="mb-2"><input type="password" class="form-control" v-model="companyRegData.password" placeholder="Password" required></div>
              <button type="submit" class="btn btn-success w-100">Register Company</button>
              <div class="mt-2 text-center"><a href="#" @click.prevent="viewMode = 'login'">Back to Login</a></div>
            </form>

            <div v-if="errorMessage" class="alert alert-danger mt-3">{{ errorMessage }}</div>
            <div v-if="successMessage" class="alert alert-success mt-3">{{ successMessage }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const viewMode = ref('login'); // 'login', 'studentReg', 'companyReg'
const errorMessage = ref('');
const successMessage = ref('');

const loginData = ref({ email: '', password: '' });
const studentRegData = ref({ full_name: '', email: '', password: '', branch: '', cgpa: '', passing_year: '' });
const companyRegData = ref({ company_name: '', hr_contact: '', website: '', email: '', password: '' });

const handleLogin = async () => {
  try {
    errorMessage.value = ''; successMessage.value = '';
    const response = await api.post('/auth/login', loginData.value);
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('role', response.data.role);
    if (response.data.role === 'student') router.push('/student');
    else if (response.data.role === 'company') router.push('/company');
    else if (response.data.role === 'admin') router.push('/admin');
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Login failed.';
  }
};

const handleStudentRegister = async () => {
  try {
    errorMessage.value = '';
    await api.post('/auth/register/student', studentRegData.value);
    successMessage.value = 'Student registered! Please login.';
    viewMode.value = 'login';
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Registration failed.';
  }
};

const handleCompanyRegister = async () => {
  try {
    errorMessage.value = '';
    await api.post('/auth/register/company', companyRegData.value);
    successMessage.value = 'Company registered! Pending admin approval.';
    viewMode.value = 'login';
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Registration failed.';
  }
};
</script>