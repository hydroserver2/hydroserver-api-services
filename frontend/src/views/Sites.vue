<template>
  <div v-if="sitesLoaded">
    <h3>My Sites</h3>
    <div style="display: flex; flex-wrap: wrap;">
      <router-link v-for="thing in ownedThings" :key="thing.id" :to="'/site/' + thing.id" style="border: 1px solid gray; padding: 10px; margin: 10px; flex-basis: 20%; transition: background-color 0.3s; display: flex; flex-direction: column; text-decoration: none;">
        <h2>{{ thing.name }}</h2>
        <p><strong>Sampling Feature Type:</strong> {{ thing.sampling_feature_type }}</p>
        <p><strong>Sampling Feature Code:</strong> {{ thing.sampling_feature_code }}</p>
        <p><strong>Site Type:</strong> {{ thing.site_type }}</p>
      </router-link>
    </div>

    <button @click="showRegisterSiteModal = true">Register a new site</button>
    <transition name="modal-fade">
      <div v-if="showRegisterSiteModal" class="modal-overlay" @click.self="showRegisterSiteModal = false">
        <register-site @close="showRegisterSiteModal = false"></register-site>
      </div>
    </transition>

    <h3>Followed Sites</h3>
    <div style="display: flex; flex-wrap: wrap;">
      <router-link v-for="thing in followedThings" :key="thing.id" :to="'/site/' + thing.id" style="border: 1px solid gray; padding: 10px; margin: 10px; flex-basis: 20%; transition: background-color 0.3s; display: flex; flex-direction: column; text-decoration: none;">
        <h4>{{ thing.name }}</h4>
        <p><strong>Latitude:</strong> {{ thing.latitude }}</p>
        <p><strong>Longitude:</strong> {{ thing.longitude }}</p>
        <p><strong>Elevation:</strong> {{ thing.elevation }}</p>
      </router-link>
    </div>
  </div>
  <div v-else>
    Loading...
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
