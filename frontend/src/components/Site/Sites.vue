<template>
  <template v-if="thingStore.loaded">
    <div class="mb-8 flex-shrink-0" style="height: 25rem">
      <GoogleMap
        :key="thingStore.ownedOrFollowedThings"
        :things="thingStore.ownedOrFollowedThings"
        v-if="thingStore.ownedOrFollowedThings"
      ></GoogleMap>
      <v-divider></v-divider>
    </div>

    <v-container>
      <v-row class="mb-4">
        <v-col cols="auto">
          <h5 class="text-h5">My Registered Sites</h5>
        </v-col>
        <v-spacer></v-spacer>
        <v-col cols="auto">
          <v-btn class="manage-metadata-button" to="Metadata" color="secondary"
            >Manage Metadata</v-btn
          >
        </v-col>
        <v-col cols="auto">
          <v-btn-secondary
            variant="elevated"
            @click="showSiteForm = true"
            prependIcon="mdi-plus"
            >Register a new site</v-btn-secondary
          >
        </v-col>
      </v-row>

      <v-data-table
        v-if="thingStore.ownedThings.length"
        :headers="headers"
        :items="thingStore.ownedThings"
        hover
        item-value="id"
        class="elevation-3"
        @click:row="onRowClick"
      >
      </v-data-table>

      <p v-else class="text-body-1 text-medium-emphasis">
        You have not registered any sites.
      </p>
    </v-container>

    <v-container class="mb-8">
      <h5 class="text-h5 mb-4">Followed Sites</h5>
      <v-data-table
        v-if="thingStore.followedThings.length"
        :headers="headers"
        :items="thingStore.followedThings"
        hover
        item-value="id"
        class="elevation-3"
        @click:row="onRowClick"
      >
      </v-data-table>
      <p v-else class="text-body-1 text-medium-emphasis">
        You are not following any sites.
      </p>
    </v-container>

    <v-dialog v-model="showSiteForm" width="60rem">
      <SiteForm @close="showSiteForm = false"></SiteForm>
    </v-dialog>
  </template>

  <div v-else>
    <v-progress-circular indeterminate color="green"></v-progress-circular>
    <p>Loading Sites...</p>
  </div>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import SiteForm from '@/components/Site/SiteForm.vue'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useThingStore } from '@/store/things'

const thingStore = useThingStore()
const showSiteForm = ref(false)
const router = useRouter()

const headers = [
  {
    title: 'Site Code',
    align: 'start',
    sortable: true,
    key: 'sampling_feature_code',
  },
  {
    title: 'Site Name',
    align: 'start',
    sortable: true,
    key: 'name',
  },
  {
    title: 'Site Type',
    align: 'start',
    sortable: true,
    key: 'site_type',
  },
]

const onRowClick = (event: Event, item: any) => {
  const thing = item.item.raw
  router.push({ name: 'SingleSite', params: { id: thing.id } })
}

onMounted(async () => {
  await thingStore.fetchThings()
})
</script>

<style scoped lang="scss"></style>
