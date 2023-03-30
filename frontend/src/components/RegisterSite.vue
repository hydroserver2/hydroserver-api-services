<template>
  <div>
    <h1>Register a Site</h1>
    <form @submit.prevent="createThing" class="form" enctype="multipart/form-data">
      <p v-for="field in formFields" :key="field.name">
        <label :for="field.id">{{ field.label }}</label>
        <input :type="field.type" v-model="formData[field.name]" :id="field.id" :name="field.name">
      </p>

      <input type="submit" value="Add Site" />
    </form>

<!--    <site-map></site-map>-->
  </div>
</template>

<script>
import axios from 'axios';
import { mapMutations } from 'vuex';
// import SiteMap from '@/components/sites/SiteMap.vue';

export default {
  // components: {
  //   SiteMap
  // },
  data() {
    return {
      formData: {
      name: "",
      description: "",
      sampling_feature_type: "",
      sampling_feature_code: "",
      site_type: "",
      latitude: null,
      longitude: null,
      elevation: null,
      city: "",
      state: "",
      country: "",
      },
    formFields: [
      { name: "name", label: "Name", type: "text" },
      { name: "description", label: "Description", type: "text" },
      { name: "sampling_feature_type", label: "Sampling Feature Type", type: "text" },
      { name: "sampling_feature_code", label: "Sampling Feature Code", type: "text" },
      { name: "site_type", label: "Site Type", type: "text" },
      { name: "latitude", label: "Latitude", type: "number" },
      { name: "longitude", label: "Longitude", type: "number" },
      { name: "elevation", label: "Elevation", type: "number" },
      { name: "city", label: "City", type: "text" },
      { name: "state", label: "State", type: "text" },
      { name: "country", label: "Country", type: "text" },
    ],
    };
  },
  methods: {
    ...mapMutations(['addThing', 'updateThing']),
    createThing() {
      axios.post('/things', this.formData)
          .then(response => {
            const newThing = response.data;
            this.addThing(newThing);
            this.$emit('close');
          })
          .catch(error => {
            console.log("Error Registering Site: ", error)
          })
    },
  },
};
</script>
