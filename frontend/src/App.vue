<script>
import { mapGetters } from 'vuex';
import Navbar from "./components/Navbar.vue";

export default {
  name: 'App',
  components: {Navbar},
  computed: {
    ...mapGetters(['isAuthenticated'])
  },
  async beforeCreate() {
    await this.$store.dispatch('loadTokens');
  },
  watch: {
    isAuthenticated(newValue) {
      console.log('isAuthenticated:', newValue);
    }
  },
};
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
