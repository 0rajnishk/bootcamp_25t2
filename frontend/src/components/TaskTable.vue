<template>
  <div>
    <h2>Task List</h2>
    <table border="1">
      <thead>
        <tr>
          <th>ID</th>
          <th>Title</th>
          <th>Description</th>
          <th>Status</th>
          <th>Deadline</th>
          <th>Assigned To</th>
          <th>Created At</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id">
          <td>{{ task.id }}</td>
          <td>{{ task.title }}</td>
          <td>{{ task.description }}</td>
          <td>
            <select :value="task.status" @change="updateTaskStatus(task.id, $event.target.value)">
              <option value="pending">Pending</option>
              <option value="inprogress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </td>
          <td>{{ task.deadline }}</td>
          <td>
            <input type="number" v-model="task.assigned_user_id" @change="$emit('reassign-task', task.id, task.assigned_user_id)">
          </td>
          <td>{{ task.created_at }}</td>
          <td>
            <button @click="$emit('delete-task', task.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'TaskTable',
  props: {
    tasks: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
th {
  background-color: #f2f2f2;
}
</style>
