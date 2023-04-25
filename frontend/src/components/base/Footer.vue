<template>
  <v-footer class="footer">
    <v-container fluid>
      <v-row class="footer-row">
        <div class="footer-column">
          <h3>Contact Us</h3>
          <p>contact</p>
          <p>Learn more about CIROH</p>
        </div>
        <div class="footer-column">
          <h3>Policies</h3>
          <p>Terms of Use</p>
          <p>Privacy</p>
        </div>
        <div class="footer-column">
          <h3>Developed By</h3>
          <img src="@/assets/UWRL.png" alt="UWRL Logo" class="uwrl-logo" />
        </div>
        <div class="footer-column">
          <h3>Open Source</h3>
          <p>
            HydroServer is open Source. Find us on
            <a
              style="color: blue"
              href="https://github.com/hydroserver2/hydroserver"
              >GitHub.</a
            >
          </p>
          <p>
            <a href="https://github.com/issues" target="_blank"
              >Report a bug here.</a
            >
          </p>
          <p>This is Version 0.4.0 of the Hydroserver web application.</p>
        </div>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script lang="ts">
export default {
  name: 'Footer',
}
</script>

<style scoped>
.footer {
  background-color: #f5f5f5;
  color: #333;
}

.footer-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-around;
}

.footer-column {
  text-align: left;
  padding: 0;
}

h3 {
  font-weight: 500;
  margin-bottom: 1rem;
}

a {
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.uwrl-logo {
  width: 100%;
  height: auto;
  max-height: 3rem;
}
</style>
