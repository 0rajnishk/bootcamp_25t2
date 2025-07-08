<template>
    Admin login

    <form @submit.prevent="login">
        <input type="email" required v-model="email">
        <input type="password" required v-model="password">
        <button>submit</button>
    </form>

    <button @click="logtoken()">click me</button>


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

            this.token = response.data
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