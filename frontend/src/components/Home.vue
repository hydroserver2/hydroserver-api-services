<template>
  <div>
    <div class="image-container">
      <v-container fluid>
        <v-row class="fill-height" no-gutters>
          <v-col
            cols="12"
            sm="6"
            class="text-container full-height d-flex align-center"
          >
            <div>
              <h1>Collect and Manage Your Operational Hydrologic Data</h1>
              <v-btn color="primary">See how it works</v-btn>
            </div>
          </v-col>
          <v-col
            cols="12"
            sm="6"
            class="cards-container full-height d-flex align-center"
          >
            <Login />
          </v-col>
        </v-row>
      </v-container>
    </div>

    <v-container fluid>
      <v-row>
        <v-col class="text-center">
          <h2>Manage your Operation Data</h2>
          <p>
            The HydroServer Hydrologic Information System provides services and
            tools for collecting, storing, managing, and sharing your hydrologic
            observations collected from in situ monitoring sites.
          </p>
        </v-col>
      </v-row>

      <v-row justify="center">
        <v-col cols="12" md="5" lg="4">
          <v-row>
            <v-col cols="2">
              <div class="icon-wrapper">
                <img :src="resistanceIcon" class="icon" alt="resistanceIcon" />
              </div>
            </v-col>
            <v-col cols="10">
              <h3>Sensor Data Streaming</h3>
              <p>
                Stream sensor data directly from your Internet connected
                datalogger or load data using our Streaming Data Loader
                software.
              </p>
            </v-col>
          </v-row>
        </v-col>

        <v-col cols="12" md="5" lg="4">
          <v-row>
            <v-col cols="2">
              <div class="icon-wrapper">
                <img :src="gearIcon" class="icon" alt="gearIcon" />
              </div>
            </v-col>
            <v-col cols="10">
              <h3>Easy Web Configuration</h3>
              <p>
                Create new monitoring locations, observed variables, sensors,
                and data streams through our web user interface.
              </p>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <v-row justify="center">
        <v-col cols="12" md="5" lg="4">
          <v-row>
            <v-col cols="2">
              <div class="icon-wrapper">
                <img :src="dbIcon" class="icon" alt="dbIcon" />
              </div>
            </v-col>
            <v-col cols="10">
              <h3>Performant Data Storage</h3>
              <p>
                Using TimeScale DB with PostgreSQL, we provide a performant data
                store for your operational data.
              </p>
            </v-col>
          </v-row>
        </v-col>

        <v-col cols="12" md="5" lg="4">
          <v-row>
            <v-col cols="2">
              <div class="icon-wrapper">
                <img :src="ogcIcon" class="icon" alt="ogcIcon" />
              </div>
            </v-col>
            <v-col cols="10">
              <h3>Open Standards Data Sharing</h3>
              <p>
                Share your data publicly using the latest Open Geospatial
                Consortium web services standard SensorThings.
              </p>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
  </div>
  <v-btn @click="sayHello">Click to say Hello</v-btn>
</template>

<script lang="ts">
import Login from '@/components/account/Login.vue'
import Signup from '@/components/account/Signup.vue'
import resistanceIcon from '@/assets/resistance.svg'
import gearIcon from '@/assets/gear.svg'
import dbIcon from '@/assets/db.svg'
import ogcIcon from '@/assets/ogc.png'
import axios from '@/plugins/axios.config'

export default {
  data() {
    return {
      resistanceIcon,
      gearIcon,
      dbIcon,
      ogcIcon,
    }
  },
  components: { Login, Signup },
  name: 'Home',
  methods: {
    async sayHello() {
      try {
        const response = await axios.post('/hello')
        console.log('Back from Server. It says', response.data)
      } catch (error) {
        console.error('Error calling /hello endpoint:', error)
      }
    },
  },
}
</script>

<style scoped lang="scss">
.image-container {
  background-image: url('@/assets/dam-background.jpg');
  background-size: cover;
  background-position: center;
  height: 40vh;
}

.text-container {
  padding: 0 5%;
  color: white;
}

.icon-wrapper {
  width: 100%;
  height: 100%;
}

.icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
