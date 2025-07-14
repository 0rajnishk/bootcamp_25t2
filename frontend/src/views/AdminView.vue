<template>
  <div class="admin-view">
    <h1>Admin Dashboard</h1>
    <p>Welcome to the admin panel. Here you can manage users and tasks.</p>
    <UserTable :users="users" @approve-user="approveUser" />
    <TaskTable :tasks="tasks" @update-task-status="updateTaskStatus" @reassign-task="reassignTask" @delete-task="deleteTask" />

    <div class="task-creation-form">
      <h2>Create New Task</h2>
      <form @submit.prevent="createTask">
        <div class="form-group">
          <label for="title">Title:</label>
          <input type="text" id="title" v-model="newTask.title" required>
        </div>
        <div class="form-group">
          <label for="description">Description:</label>
          <input type="text" id="description" v-model="newTask.description" required>
        </div>
        <div class="form-group">
          <label for="status">Status:</label>
          <select id="status" v-model="newTask.status" required>
            <option value="pending">Pending</option>
            <option value="inprogress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div class="form-group">
          <label for="deadline">Deadline:</label>
          <input type="datetime-local" id="deadline" v-model="newTask.deadline" required>
        </div>
        <div class="form-group">
          <label for="assigned_user_id">Assigned User ID:</label>
          <input type="number" id="assigned_user_id" v-model="newTask.assigned_user_id">
        </div>
        <button type="submit">Create Task</button>
      </form>
    </div>
  </div>


  <button @click="home">Home</button>
</template>

<script>
import UserTable from '@/components/UserTable.vue';
import TaskTable from '@/components/TaskTable.vue';
console.log('TaskTable imported:', TaskTable);
import axios from 'axios';

export default {
  name: 'AdminView',
  components: {
    UserTable,
    TaskTable
  },
  data() {
    return {
      users: [], // This will store actual user data from the API
      tasks: [], // This will store actual task data from the API
      newTask: {
        title: '',
        description: '',
        status: 'pending',
        deadline: '',
        assigned_user_id: null
      }
    };
  },
  async created() {
    // Fetch users when the component is created
    await this.fetchUsers();
    await this.fetchTasks();
  },
  methods: {
    async fetchUsers() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found. Please log in.');
          // Redirect to login page or show an error message
          this.$router.push('/adminlogin');
          return;
        }
        const response = await axios.get('http://127.0.0.1:5000/all_users', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        this.users = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
        // Handle error, e.g., show a message to the user
      }
    },
    async fetchTasks() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found. Please log in.');
          this.$router.push('/adminlogin');
          return;
        }
        const response = await axios.get('http://127.0.0.1:5000/task', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        this.tasks = response.data;
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    },
    async approveUser(userId) {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found. Please log in.');
          this.$router.push('/adminlogin');
          return;
        }
        await axios.put(`http://127.0.0.1:5000/admin/users/${userId}`, { is_approved: true }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        // After successful approval, re-fetch users to update the table
        await this.fetchUsers();
      } catch (error) {
        console.error('Error approving user:', error);
      }
    },
    async updateTaskStatus(taskId, newStatus) {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found. Please log in.');
          this.$router.push('/adminlogin');
          return;
        }
        await axios.put(`http://127.0.0.1:5000/task/${taskId}`, { status: newStatus }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        await this.fetchTasks(); // Re-fetch tasks to update the table
      } catch (error) {
        console.error('Error updating task status:', error);
      }
    },
    async reassignTask(taskId, newAssignedUserId) {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found. Please log in.');
          this.$router.push('/adminlogin');
          return;
        }
        await axios.put(`http://127.0.0.1:5000/task/${taskId}`, { assigned_user_id: newAssignedUserId }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        await this.fetchTasks(); // Re-fetch tasks to update the table
      } catch (error) {
        console.error('Error reassigning task:', error);
      }
    },
    async deleteTask(taskId) {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found. Please log in.');
          this.$router.push('/adminlogin');
          return;
        }
        await axios.delete(`http://127.0.0.1:5000/task/${taskId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        await this.fetchTasks(); // Re-fetch tasks to update the table
      } catch (error) {
        console.error('Error deleting task:', error);
      }
    },
    async createTask() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found. Please log in.');
          this.$router.push('/adminlogin');
          return;
        }
        // Format deadline to ISO string for backend
        // Format deadline to YYYY-MM-DD HH:MM:SS for backend
        const deadlineDate = new Date(this.newTask.deadline);
        const formattedDeadline = deadlineDate.getFullYear() + '-' +
                                  String(deadlineDate.getMonth() + 1).padStart(2, '0') + '-' +
                                  String(deadlineDate.getDate()).padStart(2, '0') + ' ' +
                                  String(deadlineDate.getHours()).padStart(2, '0') + ':' +
                                  String(deadlineDate.getMinutes()).padStart(2, '0') + ':' +
                                  String(deadlineDate.getSeconds()).padStart(2, '0');

        const formattedTask = {
          ...this.newTask,
          deadline: formattedDeadline
        };
        await axios.post('http://127.0.0.1:5000/task', formattedTask, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        this.newTask = {
          title: '',
          description: '',
          status: 'pending',
          deadline: '',
          assigned_user_id: null
        }; // Reset form
        await this.fetchTasks(); // Re-fetch tasks to update the table
      } catch (error) {
        console.error('Error creating task:', error);
      }
    },
    home() {
        this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.admin-view {
  padding: 20px;
  text-align: center;
}
h1 {
  color: #333;
}
p {
  color: #666;
}


.task-creation-form {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"],
input[type="number"],
input[type="datetime-local"] {
  width: calc(50% - 50px); /* Account for padding */
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box; /* Include padding in width */
}

button {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:hover {
  background-color: #0056b3;
}

</style>