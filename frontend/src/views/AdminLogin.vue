<template>
  <div class="login-container">
    <h2>Admin Login</h2>
    <form @submit.prevent="login" class="login-form">
      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" id="email" required v-model="email">
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" required v-model="password">
      </div>
      <button type="submit">Login</button>
    </form>
    <button @click="logtoken()" class="debug-button">Log Token</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
    data() {
        return {
            email:"",
            password:"",
            token:""
        }
    },

    methods:{
        async login() {

            const data = { "email": this.email, "password": this.password }
            const response = await axios.post("http://127.0.0.1:5000/login", data)

            this.token = response.data.access_token
            alert(this.token)
            localStorage.setItem("token", this.token)
            this.$router.push("/admin")
        },

        logtoken(){
            alert(this.token)
            alert(localStorage.getItem("token"))
        }

    }

}

</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh; /* Adjust as needed for vertical centering */
  background-color: #f4f4f4;
  padding: 20px;
}

.login-form {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
}

input[type="email"],
input[type="password"] {
  width: calc(100% - 20px); /* Account for padding */
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box; /* Include padding in width */
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

button:hover {
  background-color: #0056b3;
}

.debug-button {
  margin-top: 20px;
  background-color: #6c757d;
}

.debug-button:hover {
  background-color: #5a6268;
}
</style>