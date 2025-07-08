<template>
    <h2>home view</h2>
    <button @click="hello" >click me</button>

    <p>{{ msg }}</p>
    <!-- button to redirect to /admin -->
    <button @click="admin">Admin</button>

</template>

<script>
import axios from "axios";

export default {

    data() {
        return {
            msg: ""
        }
    },


methods: {
 async hello(){
        // alert("this is an alert")
        const response = await axios.get("http://127.0.0.1:5000/");
        this.msg = response.data
    },
    admin() {
        this.$router.push('/admin')
    }
},

// beforeCreate() {
//     alert("this is before create")
// },

created() {
    alert("this is created")
    this.hello()
},


mounted() {
    alert("this is mounted")
},

unmounted() {
    alert("this is unmounted")
},



}

</script>