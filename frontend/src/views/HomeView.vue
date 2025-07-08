<template>
    <h2>home view</h2>
    <button @click="hello" >click me</button>

    <p>{{ msg }}</p>


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
    }
},

beforeCreate() {
    alert("this is before create")
},

created() {
    alert("this is created")
},


mounted() {
    this.hello()
},

unmounted() {
    alert("this is unmounted")
},



}

</script>