<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="4">
        <h1>Browse Data Collection Sites</h1>
        <v-btn color="teal-lighten-1" @click="clearFilters">Clear Filters</v-btn><br><br>
        <v-expansion-panels class="custom-expansion-panel">
          <v-expansion-panel title="Site Types" color="teal-lighten-1">
            <v-expansion-panel-text>
               <template v-for="type in siteTypes" :key="type">
                <v-checkbox
                  :label="type"
                  v-model="selectedSiteTypes"
                  :value="type"
                />
              </template>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
      <v-col cols="12" md="8">
        <GoogleMap :markers="markers" v-if="markers" :mapOptions="{center: {lat: 39, lng: -100}, zoom: 4}" style="width: 100%; height: 80vh" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import GoogleMap from '@/components/GoogleMap.vue';
import {useDataStore} from "@/store/data.js";
import {ref, watch} from "vue";

export default {
  components: { GoogleMap },
  setup() {
    const dataStore = useDataStore()
    const siteTypes = ref(['Atmosphere', 'Ditch', 'Lake', 'Ocean', 'River', 'Spring', 'Stream', 'Wetland', 'Well', 'Other'])
    const selectedSiteTypes = ref([])
    const markers = ref(null)

    function clearFilters() { selectedSiteTypes.value = [] }

    dataStore.fetchOrGetFromCache('things', '/things').then(() => {
      markers.value = dataStore.things
    })

    return { siteTypes, selectedSiteTypes, markers, clearFilters };
  }
}
</script>
