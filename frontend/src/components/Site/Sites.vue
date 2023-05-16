<template>
  <div v-if="markerStore.loaded">
    <GoogleMap :markers="markerStore.ownedOrFollowedMarkers"></GoogleMap>
    <hr />
    <div
      style="display: flex; justify-content: space-between; align-items: center"
    >
      <h2 style="margin: 1rem">My Registered Sites</h2>
      <div>
        <v-btn to="Metadata" color="grey" style="margin: 1rem"
          >Manage Metadata</v-btn
        >
        <v-btn @click="showSiteForm = true" color="green" style="margin: 1rem"
          >Register a new site</v-btn
        >
      </div>
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
        <tr
          v-for="marker in markerStore.ownedMarkers"
          :key="marker.id"
          @click="
            $router.push({ name: 'SingleSite', params: { id: marker.id } })
          "
          class="row-bordered"
        >
          <td>{{ marker.sampling_feature_code }}</td>
          <td>{{ marker.name }}</td>
          <td>{{ marker.site_type }}</td>
        </tr>
      </tbody>
    </v-table>

    <transition name="modal-fade">
      <div
        v-if="showSiteForm"
        class="modal-overlay"
        @click.self="showSiteForm = false"
      >
        <v-dialog v-model="showSiteForm" width="80rem">
          <SiteForm @close="showSiteForm = false"></SiteForm>
        </v-dialog>
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
        <tr
          v-for="marker in markerStore.followedMarkers"
          :key="marker.id"
          @click="
            $router.push({ name: 'SingleSite', params: { id: marker.id } })
          "
          class="row-bordered"
        >
          <td>{{ marker.sampling_feature_code }}</td>
          <td>{{ marker.name }}</td>
          <td>{{ marker.site_type }}</td>
        </tr>
      </tbody>
    </v-table>
  </div>

  <div
    v-else
    style="
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    "
  >
    <v-progress-circular indeterminate color="green"></v-progress-circular>
    <p>Loading Sites...</p>
  </div>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import SiteForm from '@/components/Site/SiteForm.vue'
import { ref, onMounted } from 'vue'
import { useMarkerStore } from '@/store/markers'

const markerStore = useMarkerStore()
const showSiteForm = ref(false)

onMounted(async () => {
  await markerStore.fetchMarkers()
})
</script>

<style scoped lang="scss">
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
