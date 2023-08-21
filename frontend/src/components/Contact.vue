<template>
  <v-container class="d-flex flex-column justify-start">
    <v-row class="d-flex justify-start mb-6 mt-4">
      <v-col class="d-flex d-flex justify-start">
        <v-card-text class="d-flex justify-start align-center flex-column">
          <h4 class="text-h4 mb-4">Contact Us</h4>
          <h5 class="text-h5">
            Have questions about our software or development? We'd love to hear
            from you.
          </h5>
        </v-card-text>
      </v-col>
    </v-row>

    <v-row class="d-flex align-start justify-start" align="stretch">
      <v-col cols="12" md="6" class="align-self-start">
        <v-card class="fill-height d-flex flex-column justify-space-between">
          <v-card-text>
            <h5 class="text-h5 mb-4 d-flex align-center">
              <v-icon left color="grey-darken-1">mdi-email</v-icon>Email Us
            </h5>
            The HydroServer software is under development at the Utah Water
            Research Laboratory at Utah State University through support from
            the National Oceanic and Atmospheric Administration’s (NOAA)
            Cooperative Institute for Research to Operations in Hydrology
            (CIROH). Please contact Jeff Horsburgh at jeff.horsburgh@usu.edu
          </v-card-text>
          <v-card-actions class="justify-end">
            <v-btn-secondary href="mailto:jeff.horsburgh@usu.edu">
              Send an email
            </v-btn-secondary>
          </v-card-actions>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="fill-height d-flex flex-column justify-space-between">
          <v-card-text>
            <h5 class="text-h5 mb-4 d-flex align-center">
              <v-icon left color="grey-darken-1">mdi-github</v-icon>Connect With
              Us on GitHub
            </h5>
            All of our software development activities are open source and
            available in GitHub. You can submit bugs or issues and follow our
            software development activities on our repo
          </v-card-text>

          <v-card-actions class="justify-end">
            <v-btn-primary
              href="https://github.com/orgs/hydroserver2/repositories"
            >
              Go to Github
            </v-btn-primary>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts"></script>
