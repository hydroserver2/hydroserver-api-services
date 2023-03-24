<template>
  <div v-if="userData || loading">
    <h3>My Sites</h3>
    <div style="display: flex; flex-wrap: wrap;">
      <div v-for="thing in ownedThings" :key="thing.id" style="border: 1px solid gray; padding: 10px; margin: 10px; flex-basis: 20%; transition: background-color 0.3s;">
        <router-link :to="'/site/' + thing.id">
          <h4>{{ thing.name }}</h4>
<!--          <p><strong>Number of Datastreams:</strong> {{ thing.datastreams.length }}</p>-->
          <p><strong>Sampling Feature Type:</strong> {{ thing.sampling_feature_type }}</p>
          <p><strong>Sampling Feature Code:</strong> {{ thing.sampling_feature_code }}</p>
          <p><strong>Site Type:</strong> {{ thing.site_type }}</p>
        </router-link>
      </div>
    </div>
    <h3>Followed Sites</h3>
    <div style="display: flex; flex-wrap: wrap;">
      <div v-for="thing in followedThings" :key="thing.id" style="border: 1px solid gray; padding: 10px; margin: 10px; flex-basis: 20%; transition: background-color 0.3s;">
        <router-link :to="'/site/' + thing.id">
          <h4>{{ thing.name }}</h4>
<!--          <p><strong>Number of Datastreams:</strong> {{ thing.datastreams.length }}</p>-->
          <p><strong>Latitude:</strong> {{ thing.latitude }}</p>
          <p><strong>Longitude:</strong> {{ thing.longitude }}</p>
          <p><strong>Elevation:</strong> {{ thing.elevation }}</p>
        </router-link>
      </div>
    </div>
  </div>
  <div v-else>
    Loading...
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'Sites',
  computed: {
    ...mapState(['userData']),
    ownedThings() {
      if (!this.userData) {
        const userData = JSON.parse(localStorage.getItem('userData'));
        if (userData) {
          return userData.owned_things;
        }
        return [];
      }
      return JSON.parse(this.userData).owned_things;
    },
    followedThings() {
      if (!this.userData) {
        const userData = JSON.parse(localStorage.getItem('userData'));
        if (userData) {
          return userData.followed_things;
        }
        return [];
      }
      return JSON.parse(this.userData).followed_things;
    },
    loading() {
      return !this.userData && !localStorage.getItem('userData');
    },
  },
  created() {
    this.$store.dispatch('fetchUserData')
      .catch(error => {
        console.log(error);
      });
  },
};
</script>

<style scoped>
</style>
