<template>
  <div style="margin: 1rem">
    <table>
      <thead>
        <tr style="background-color: lightgrey">
          <th v-for="(nameTuple, index) in names" :key="index">
            {{ nameTuple[1] }}
          </th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td v-for="(nameTuple, index) in names" :key="index">
            {{ row[nameTuple[0]] }}
          </td>
          <td class="action-slot">
            <slot name="actions" :row="row"></slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts" setup>
const props = defineProps({
  title: String,
  names: Array,
  rows: Array,
})
</script>

<style lang="scss">
table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 1rem;
  border: 1px solid lightgray;
  //border-bottom: 1px solid lightgray;
  border-collapse: collapse;
  border-spacing: 0;
  margin-left: auto;
  margin-right: auto;
}

table th,
table td {
  padding: 0.1rem;
  vertical-align: middle;
  border-top: 1px solid #dee2e6;
}

table thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
}

table tbody + tbody {
  border-top: 2px solid #dee2e6;
}

table th {
  font-weight: 500;
  text-align: left;
}

table tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.05);
}

.action-link-separator {
  margin-left: 5px;
  margin-right: 5px;
}

.action-slot a {
  color: #007bff;
  text-decoration: none;
  cursor: pointer;
}

.action-slot a:hover {
  color: #0056b3;
  text-decoration: underline;
}

.action-slot a + a {
  margin-left: 10px;
}
</style>
