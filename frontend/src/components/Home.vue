<template>
  <div>
    <div class="image-container">
      <div
        class="text-container full-height d-flex flex-column justify-center align-start"
      >
        <h1 style="margin-bottom: 1.5rem">
          Collect and Manage Your Operational Hydrologic Data
        </h1>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed imperdiet
          justo augue, vel dapibus massa mattis ac. Nulla congue rhoncus velit,
          nec lobortis mauris pulvinar non. Donec nec vestibulum mauris.
        </p>
        <v-btn
          color="green-darken-2"
          variant="outlined"
          style="margin-top: 1.5rem"
        >
          <i class="fas fa-play"></i>
          How it works</v-btn
        >
      </div>
    </div>

    <hr />
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
  <hr />
  <h2 style="margin-bottom: 1.5rem; margin-top: 5rem">
    Operational Data for Modeling
  </h2>
  <h4 style="margin-bottom: 1.5rem">
    Your data can improve NOAA's water prediction services
  </h4>
  <p style="margin-bottom: 5rem">
    NOAA's National Water Model can assimilate streamflow data from operational
    monitoring sites like yours. Contribute your streamflow data to make it
    available to support continental-scale hydrologic modeling and forecasting
    via the National Water Model.
  </p>

  <hr />
  <h2 style="margin-bottom: 1.5rem; margin-top: 3rem">
    Open Standards Data Sharing
  </h2>
  <p style="margin-bottom: 5rem">
    Share your data publicly using the latest Open Geospatial Consortium web
    services standard SensorThings.
  </p>
  <!--  <v-btn @click="sayHello">Click to say Hello</v-btn>-->
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
  background: white;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  position: relative;
  height: 60vh;
}

.text-container {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50%;
  padding: 0 20px;
  box-sizing: border-box;
}

@media only screen and (max-width: 767px) {
  .text-container {
    width: 100%;
    position: static;
    transform: none;
    margin-top: 20px;
  }
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

i.fas.fa-play {
  padding-right: 1rem;
}
</style>
