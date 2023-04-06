<template>
  <div v-if="isLoaded">
    <GoogleMap :markers="[thing]" :mapOptions="mapOptions"/>

    <div class="site-information-container">
      <h2 class="site-information-title">Site Information</h2>
      <v-btn color="green">Edit Site Information</v-btn>
    </div>

    <div class="content-wrapper">
      <div class="table-container">
        <table>
          <tr>
            <td><i class="fas fa-info-circle"></i> Name</td>
            <td>{{ displayThing?.name }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-id-badge"></i> ID</td>
            <td>{{ displayThing?.id }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-file-alt"></i> Description</td>
            <td>{{ displayThing?.description }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map-marker-alt"></i> Sampling Feature Type</td>
            <td>{{ displayThing?.sampling_feature_type }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-barcode"></i> Sampling Feature Code</td>
            <td>{{ displayThing?.sampling_feature_code }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map-pin"></i> Site Type</td>
            <td>{{ displayThing?.site_type }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map"></i> Latitude</td>
            <td>{{ displayThing?.latitude }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map"></i> Longitude</td>
            <td>{{ displayThing?.longitude }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-mountain"></i> Elevation</td>
            <td>{{ displayThing?.elevation }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-users"></i> Followers</td>
            <td>{{ displayThing?.followers }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-user-check"></i> Is Primary Owner</td>
            <td>{{ displayThing?.is_primary_owner ? 'Yes' : 'No' }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-user"></i> Owns Thing</td>
            <td>{{ displayThing?.owns_thing ? 'Yes' : 'No' }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-user-friends"></i> Follows Thing</td>
            <td>{{ displayThing?.follows_thing ? 'Yes' : 'No' }}</td>
          </tr>
        </table>
      </div>
      <ImageCarousel :carousel-items="carouselItems" />
    </div>
  </div>

  <div class="site-information-container">
    <h2 class="site-information-title">Datastreams Available at this Site</h2>
    <v-btn color="grey-lighten-2">Manage Datastreams</v-btn>
    <img src="@/assets/hydro.png" alt="hydro" class="site-information-image">
    <v-btn color="grey-lighten-2" class="site-information-button">Download Data from HydroShare</v-btn>
  </div>

  <v-row class="ma-2">
    <v-col md="3" class="pa-3 d-flex flex-column" v-for="datastream in displayThing?.datastreams" :key="datastream.id">
      <v-card class="elevation-5 flex d-flex flex-column" outlined>
        <v-card-title>{{ datastream.name }}</v-card-title>
      </v-card>
    </v-col>
  </v-row>

</template>

<script>
import GoogleMap from "../components/GoogleMap.vue";
import ImageCarousel from "../components/ImageCarousel.vue";
import MoonIm1 from "@/assets/moon_bridge1.jpg"
import MoonIm2 from "@/assets/moon_bridge2.jpg"
import MoonIm3 from "@/assets/moon_bridge3.jpg"

export default {
  name: "SingleSite",
  components: {
    GoogleMap,
    ImageCarousel,
  },
  computed: {
    displayThing() {
      return this.thing;
    },
     isLoaded() {
      return this.thing;
    },
    mapOptions() {
    return this.thing ? {
          center: { lat: this.thing.latitude, lng: this.thing.longitude },
          zoom: 16,
          mapTypeId: "satellite"
        } : null;
  },
  },
   props: {
     id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      thing: null,
      currentSlide: 0,
      carouselItems: [
        {
          src: MoonIm1,
          alt: "Moon1"
        },
        {
          src: MoonIm2,
          alt: "Moon2"
        },
        {
          src: MoonIm3,
          alt: "Moon3"
        },
      ],
    }
  },
  methods: {
    prevSlide() {
      this.currentSlide = this.currentSlide === 0 ? this.carouselItems.length - 1 : this.currentSlide - 1;
    },
    nextSlide() {
      this.currentSlide = (this.currentSlide + 1) % this.carouselItems.length;
    },
    setSlide(index) {
      this.currentSlide = index;
    },
  },
  async mounted() {
    console.log("Mounting SingleSite. ID: ", this.id)
    try {
      let cacheName = `thing_${this.id}`
      await this.$store.dispatch("fetchOrGetFromCache", {key: cacheName, apiEndpoint: `/things/${this.id}`});
      this.thing = this.$store.state[cacheName];
    } catch (error) {
      console.error("Error fetching thing data from API", error);
    }
    console.log("Thing: ", this.thing)
  },
};
</script>

<style scoped>
 .site-information-image {
   margin-left: auto;
   margin-right: 1rem;
   max-height: 30px;
}

.title-button-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.hydroshare-logo-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.hydroshare-logo-container img {
  max-height: 50px;
}

table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 1rem;
   border-right: 1px solid lightgray;
  border-bottom: 1px solid lightgray;
  border-collapse: collapse;
  border-spacing: 0;
  margin-left: auto;
  margin-right: auto;
}

table th,
table td {
  padding: 0.1rem; /* Adjusted padding to make elements shorter */
  vertical-align: middle;
  border-top: 1px solid #dee2e6;
}

table thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
}

table tbody + tbody {
  border-top: 2px solid #dee2e6;
}

table th {
  font-weight: 500;
  text-align: left;
}

table tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.05);
}

 table td:first-child {
  display: flex;
  align-items: center;
  white-space: nowrap;
  background-color: #f5f5f5;
  text-align: left; /* Added to align text to the left */
}

table td:first-child i {
  margin-right: 0.5rem;
  width: 1.5rem; /* Set a fixed width for the icons */
  text-align: center; /* Center the icons within the fixed width */
}

table td:last-child {
  background-color: #ffffff; /* Set background color for right td */
}

table td:first-child i {
  margin-right: 0.5rem;
}

.site-information-container {
  padding: 1rem;
  display: flex;
  align-items: center;
}

.site-information-title{
  margin-right: 2rem;
}

.content-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.content-wrapper > * {
  max-height: 30vh;
}

.table-container {
  width: 60%;
  position: relative;
}

.carousel-container {
  width: calc(40% - 1rem); /* Subtract the gap from the width */
  position: relative;
}


</style>
