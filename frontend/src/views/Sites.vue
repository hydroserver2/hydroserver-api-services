<template>
  <div v-if="sitesLoaded">
    <GoogleMap :markers="markers" v-if="markers"></GoogleMap>
    <hr>
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h2 style="margin: 1rem">My Registered Sites</h2>
      <v-btn @click="showRegisterSiteModal = true" color="green" style="margin: 1rem">Register a new site</v-btn>
    </div>
    <v-table :hover="true" class="table-bordered">
        <thead style="background-color: lightgrey">
          <tr class="header-bordered">
            <th><strong>Site Code</strong></th>
            <th>Site Name</th>
            <th>Site Type</th>
          </tr>
        </thead>
        <tbody style="border: 1px black">
          <tr v-for="thing in ownedThings"
              :key="thing.id"
              @click="$router.push({ name: 'SingleSite', params: { id: thing.id } })"
              class="row-bordered">
            <td>{{ thing.sampling_feature_code }}</td>
            <td>{{ thing.name }}</td>
            <td>{{ thing.site_type }}</td>
          </tr>
        </tbody>
    </v-table>

    <transition name="modal-fade">
      <div v-if="showRegisterSiteModal" class="modal-overlay" @click.self="showRegisterSiteModal = false">
        <site-form @close="showRegisterSiteModal = false" @siteCreated="updateMarkers"></site-form>
      </div>
    </transition>

    <h2 style="margin: 1rem">Followed Sites</h2>
    <v-table :hover="true" class="table-bordered">
        <thead style="background-color: lightgrey">
          <tr class="header-bordered">
            <th><strong>Site Code</strong></th>
            <th>Site Name</th>
            <th>Site Type</th>
          </tr>
        </thead>
        <tbody style="border: 1px black">
          <tr v-for="thing in followedThings"
              :key="thing.id"
              @click="$router.push({ name: 'SingleSite', params: { id: thing.id } })"
              class="row-bordered">
            <td>{{ thing.sampling_feature_code }}</td>
            <td>{{ thing.name }}</td>
            <td>{{ thing.site_type }}</td>
          </tr>
        </tbody>
    </v-table>
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

.table-bordered {
  margin: 1rem;
  border-collapse: collapse;
  border: 1px solid lightgrey;
}

.row-bordered th,
.row-bordered td {
  border: 1px solid #e8e8e8;
  padding: 8px;
  width: 33.33%;
}

.header-bordered th,
.header-bordered td {
  border: 1px solid #c5c5c5;
  padding: 8px;
}

.row-bordered:hover {
  cursor: pointer;
}
</style>
