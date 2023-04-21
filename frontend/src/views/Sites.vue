<template>
  <div v-if="sitesLoaded">
    <hr>
    <GoogleMap :markers="markers" v-if="markers"></GoogleMap>
    <hr>
    <h2>My Registered Sites</h2>
    <v-btn @click="showRegisterSiteModal = true" color="green">Register a new site</v-btn>
    <v-row class="ma-2">
      <v-col md="3" class="pa-3 d-flex flex-column" v-for="thing in ownedThings" :key="thing.id">
        <v-card :to="{name: 'SingleSite', params: { id: thing.id}}" class="elevation-5 flex d-flex flex-column" variant="outlined">
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
        <site-form @close="showRegisterSiteModal = false" @siteCreated="updateMarkers"></site-form>
      </div>
    </transition>

    <h3>Followed Sites</h3>
    <v-row class="ma-2">
      <v-col md="3" class="pa-3 d-flex flex-column" v-for="thing in followedThings" :key="thing.id">
        <v-card :to="{name: 'SingleSite', params: { id: thing.id}}" class="elevation-5 flex d-flex flex-column" variant="outlined">
          <v-card-title class="text-h5">{{ thing.name }}</v-card-title>
          <v-card-text class="flex">
            <div><strong>Sampling Feature Type:</strong> {{ thing.sampling_feature_type }}</div>
            <div><strong>Sampling Feature Code:</strong> {{ thing.sampling_feature_code }}</div>
            <div><strong>Site Type:</strong> {{ thing.site_type }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>

<div v-else style="display: flex; justify-content: center; align-items: center; height: 100vh;">
  <v-progress-circular indeterminate color="green"></v-progress-circular>
  <p>Loading Sites...</p>
</div>
</template>

<script>
import { ref, computed } from 'vue';
import GoogleMap from '@/components/GoogleMap.vue';
import { useDataStore } from '@/store/data.js';
import SiteForm from "@/components/Site/SiteForm.vue";

export default {
  name: 'Sites',
  components: {
    SiteForm,
    GoogleMap,
  },
  setup() {
    const dataStore = useDataStore()
    const showRegisterSiteModal = ref(false)
    const ownedThings = ref([])
    const followedThings = ref([])
    const markers = ref(null)

    const sitesLoaded = computed(() => ownedThings.value && followedThings.value)

    async function updateMarkers() {
      await dataStore.fetchOrGetFromCache('things', '/things')
      ownedThings.value = dataStore.things.filter((thing) => thing.owns_thing)
      followedThings.value = dataStore.things.filter((thing) => thing.follows_thing)
      markers.value = [...ownedThings.value, ...followedThings.value]
    }

    updateMarkers()

    return { showRegisterSiteModal, ownedThings, followedThings, markers, sitesLoaded, updateMarkers }
  }
}
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

.modal-fade-enter {
  opacity: 0;
}
</style>
