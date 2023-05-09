<template>
  <template v-if="sitesLoaded">
    <div class="mb-8 flex-shrink-0" style="height: 25rem">
      <GoogleMap :markers="markers" v-if="markers"></GoogleMap>
      <v-divider></v-divider>
    </div>

    <v-container>
      <div class="d-flex justify-space-between mb-4">
        <h5 class="text-h5">My Registered Sites</h5>
        <v-btn
          color="green"
          variant="elevated"
          density="comfortable"
          @click="showSiteForm = true"
          prependIcon="mdi-plus"
          >Register a new site</v-btn
        >
      </div>

      <v-table v-if="ownedThings.length" class="mb-12">
        <thead>
          <tr>
            <th><strong>Site Code</strong></th>
            <th>Site Name</th>
            <th>Site Type</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="thing in ownedThings"
            :key="thing.id"
            @click="
              $router.push({ name: 'SingleSite', params: { id: thing.id } })
            "
          >
            <td>{{ thing.sampling_feature_code }}</td>
            <td>{{ thing.name }}</td>
            <td>{{ thing.site_type }}</td>
          </tr>
        </tbody>
      </v-table>
      <p v-else class="text-body-1 text-medium-emphasis">
        You have not registered any sites.
      </p>
    </v-container>

    <v-container class="mb-8">
      <h5 class="text-h5 mb-4">Followed Sites</h5>
      <v-table
        v-if="followedThings.length"
        :hover="true"
        class="table-bordered"
      >
        <thead>
          <tr class="header-bordered">
            <th><strong>Site Code</strong></th>
            <th>Site Name</th>
            <th>Site Type</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="thing in followedThings"
            :key="thing.id"
            @click="
              $router.push({ name: 'SingleSite', params: { id: thing.id } })
            "
            class="row-bordered"
          >
            <td>{{ thing.sampling_feature_code }}</td>
            <td>{{ thing.name }}</td>
            <td>{{ thing.site_type }}</td>
          </tr>
        </tbody>
      </v-table>
      <p v-else class="text-body-1 text-medium-emphasis">
        You are not following any sites.
      </p>
    </v-container>

    <v-dialog v-model="showSiteForm" width="60rem">
      <site-form
        @close="showSiteForm = false"
        @siteCreated="updateMarkers"
      ></site-form>
    </v-dialog>
  </template>

  <div v-else>
    <v-progress-circular indeterminate color="green"></v-progress-circular>
    <p>Loading Sites...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import GoogleMap from '@/components/GoogleMap.vue'
import { useDataStore } from '@/store/data'
import SiteForm from '@/components/Site/SiteForm.vue'
import { onMounted } from 'vue'

const dataStore = useDataStore()
const ownedThings = ref([])
const followedThings = ref([])
const markers = ref(null)
const showSiteForm = ref(false)

const sitesLoaded = computed(() => ownedThings.value && followedThings.value)

async function updateMarkers() {
  await dataStore.fetchOrGetFromCache('things', '/things')
  ownedThings.value = dataStore.things.filter((thing) => thing.owns_thing)
  followedThings.value = dataStore.things.filter((thing) => thing.follows_thing)
  markers.value = [...ownedThings.value, ...followedThings.value]
}

onMounted(() => {
  updateMarkers()
})
</script>

<style scoped lang="scss"></style>
