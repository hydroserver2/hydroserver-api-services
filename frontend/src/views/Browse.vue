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
        <GoogleMap :markers="markers" :mapOptions="{center: {lat: 39, lng: -100}, zoom: 4}" style="width: 100%; height: 80vh" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import GoogleMap from '@/components/GoogleMap.vue';

export default {
  components: {
    GoogleMap,
  },
  data() {
    return {
      siteTypes: ['Atmosphere', 'Ditch', 'Lake', 'Ocean', 'River', 'Spring', 'Stream', 'Wetland', 'Well', 'Other'],
      selectedSiteTypes: [],
      markers: [],
    };
  },
  methods: {
    clearFilters() {
      this.selectedSiteTypes = [];
    },
    async updateMarkers() {
      await this.$store.dispatch("fetchOrGetFromCache", {key: "things", apiEndpoint: "/things"});
      this.markers = this.$store.state.things;
    },
  },
  mounted() {
    this.updateMarkers()
  },
  watch: {
    selectedSiteTypes: {
      handler(newValue) {
        console.log('selectedSiteTypes:', newValue);
      },
      deep: true,
    },
  },
};
</script>

<style>
.custom-expansion-panel .v-expansion-panel--active {
  background-color: rgb(250, 250, 250);
}
</style>
