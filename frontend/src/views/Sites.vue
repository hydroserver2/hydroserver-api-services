<template>
  <div v-if="sitesLoaded">
    <h1>My Sites</h1>
    <hr><hr>
    <h2>My Registered Sites</h2>
    <v-btn @click="showRegisterSiteModal = true" color="green">Register a new site</v-btn>
    <v-row class="ma-2">
      <v-col md="3" class="pa-3 d-flex flex-column" v-for="thing in ownedThings" :key="thing.id">
        <v-card to="'/site/' + thing.id" class="elevation-5 flex d-flex flex-column" variant="outlined">
          <v-card-title class="text-h5">{{ thing.name }}</v-card-title>
          <v-card-text class="flex">
            <div><strong>Sampling Feature Type:</strong> {{ thing.sampling_feature_type }}</div>
            <div><strong>Sampling Feature Code:</strong> {{ thing.sampling_feature_code }}</div>
            <div><strong>Site Type:</strong> {{ thing.site_type }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <transition name="modal-fade">
      <div v-if="showRegisterSiteModal" class="modal-overlay" @click.self="showRegisterSiteModal = false">
        <register-site @close="showRegisterSiteModal = false"></register-site>
      </div>
    </transition>

    <h3>Followed Sites</h3>
    <v-row class="ma-2">
      <v-col md="4" class="pa-3 d-flex flex-column" v-for="thing in followedThings" :key="thing.id">
        <v-card class="elevation-5 flex d-flex flex-column">
          <v-card-text>
            <p><strong>Latitude:</strong> {{ thing.latitude }}</p>
            <p><strong>Longitude:</strong> {{ thing.longitude }}</p>
            <p><strong>Elevation:</strong> {{ thing.elevation }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>

<div v-else style="display: flex; justify-content: center; align-items: center; height: 100vh;">
  <v-progress-circular indeterminate color="green"></v-progress-circular>
  <P>Loading Sites...</P>
</div>
</template>

<script>
import RegisterSite from '../components/RegisterSite.vue';

export default {
  name: 'Sites',
  components: {
    RegisterSite
  },
  data() {
    return {
      showRegisterSiteModal: false,
      ownedThings: [],
      followedThings: [],
    };
  },
  computed: {
    sitesLoaded() { return this.ownedThings && this.followedThings }
  },
  created() {
    console.log("Creating Sites page...")
    this.$store.dispatch('fetchOrGetFromCache', {key: 'things', apiEndpoint: '/things'})
        .then(() => {
          this.ownedThings = this.$store.state.things.filter(thing => thing.owns_thing);
          this.followedThings = this.$store.state.things.filter(thing => thing.followed_thing);
          console.log("Owned Things: ", this.ownedThings)
          console.log("Followed Things", this.followedThings)
        })
        .catch(error => { console.log(error) });
  }
};
</script>


<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-fade-enter,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s;
}
</style>
