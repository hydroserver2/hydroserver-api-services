<template>
  <v-dialog v-model="dialog" width="95%" @click:outside="closeDialog">
    <v-card>
      <v-card-title class="text-h5">
        Register a Site
        <v-spacer></v-spacer>
      </v-card-title>
      <v-card-text>
        <v-container fluid>
          <v-row>
            <v-col cols="12" md="6">
              <v-form ref="form" @submit.prevent="createThing" enctype="multipart/form-data">
                <v-text-field label="Site Code" v-model="formData.sampling_feature_code" />
                <v-text-field label="Site Name" v-model="formData.name" />
                <v-textarea label="Site Description" v-model="formData.description" />
                <v-text-field label="Site Type" v-model="formData.site_type" />
              </v-form>
            </v-col>
            <v-col cols="12" md="6">
              <GoogleMap clickable @location-clicked="onMapLocationClicked"
                         :markers="[]" :mapOptions="{center: {lat: 39, lng: -100}, zoom: 4}" />
              Click on the map to update site coordinates and elevation data.
              <br><br><br><h2>Site Location</h2><br>
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field label="Latitude" v-model="formData.latitude" type="number" />
                  <v-text-field label="Elevation" v-model="formData.elevation" type="number" />
                  <v-text-field label="State" v-model="formData.state" />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field label="Longitude" v-model="formData.longitude" type="number" />
                  <v-text-field label="Elevation Datum" v-model="formData.elevation_datum" />
                  <v-text-field label="Country" v-model="formData.country" />
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="error" @click="closeDialog">Cancel</v-btn>
        <v-btn color="primary" @click="createThing">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref } from 'vue';
import axios from "@/axiosConfig"
import { useDataStore } from "@/store/data.js";
import GoogleMap from "./GoogleMap.vue";

export default {
  components: { GoogleMap },
  setup(props, ctx) {
    const dialog = ref(true);
    const formData = ref({
      name: "",
      description: "",
      sampling_feature_type: "",
      sampling_feature_code: "",
      site_type: "",
      latitude: null,
      longitude: null,
      elevation: null,
      state: "",
      country: ""
    })
    const formFields = [
      { name: "name", label: "Name", type: "text" },
      { name: "description", label: "Description", type: "text" },
      { name: "sampling_feature_type", label: "Sampling Feature Type", type: "text" },
      { name: "sampling_feature_code", label: "Sampling Feature Code", type: "text" },
      { name: "site_type", label: "Site Type", type: "text" },
      { name: "latitude", label: "Latitude", type: "number" },
      { name: "longitude", label: "Longitude", type: "number" },
      { name: "elevation", label: "Elevation", type: "number" },
      { name: "state", label: "State", type: "text" },
      { name: "country", label: "Country", type: "text" },
    ];

    function closeDialog() {
      dialog.value = false;
      ctx.emit("close");
    }

    function createThing() {
      axios.post('/things', formData.value)
        .then(response => {
          const newThing = response.data;
          const dataStore = useDataStore();
          dataStore.addThing(newThing);
          ctx.emit('close');
          ctx.emit('siteCreated');
        })
        .catch(error => {console.log("Error Registering Site: ", error)})
    }

    function onMapLocationClicked(locationData) {
      formData.value.latitude = locationData.latitude;
      formData.value.longitude = locationData.longitude;
      formData.value.elevation = locationData.elevation;
      formData.value.nearest_town = locationData.nearest_town;
      formData.value.state = locationData.state;
      formData.value.country = locationData.country;
    }

    return { dialog, formData, formFields, closeDialog, createThing, onMapLocationClicked }
  }
};
</script>
