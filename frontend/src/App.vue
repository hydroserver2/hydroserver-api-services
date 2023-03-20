<script setup>
import Navbar from "./components/Navbar.vue";
import Home from "./components/Home.vue";
</script>

<template>
  <header>
    <Navbar/>
  </header>
  <main>
    <router-view></router-view>
  </main>
</template>

<style scoped>
</style>
