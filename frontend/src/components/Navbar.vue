<template>
  <div class="container container--narrow">
    <nav class="header__nav">
      <router-link to="/" class="header__logo"><img src="" alt="Hydro Server Logo" /></router-link>
      <ul class="header__menu">
        <li class="header__menuItem"><router-link to="/sites">My Sites</router-link></li>
        <li class="header__menuItem"><router-link to="/signup">Signup</router-link></li>
        <li class="header__menuItem"><a href="">Browse</a></li>
        <li class="header__menuItem"><a href="">Time Series Visualization</a></li>

        <li class="header__menuItem" v-if="isAuthenticated"><a href="">Account</a></li>
        <li class="header__menuItem" v-if="isAuthenticated"><a href="" class="btn btn--sub" @click.prevent="logout">Logout</a></li>
        <li class="header__menuItem" v-else><a href="" class="btn btn--sub">Login/Sign Up</a></li>
      </ul>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'Navbar',
  data() {
    return {
      isAuthenticated: true,
    };
  },
};
</script>

<style scoped>
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #27ae60;
  padding: 1rem;
}

ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.header__menuItem {
  margin-right: 1rem;
}

.header__menuItem a {
  color: #fff;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
}

.header__menuItem a:hover {
  color: #2ecc71;
}

.btn {
  display: inline-block;
  background-color: #3498db;
  color: #fff;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

.btn--sub {
  background-color: #2980b9;
}

.btn:hover {
  background-color: #2980b9;
}
</style>