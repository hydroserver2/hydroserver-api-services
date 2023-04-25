<template>
  <div class="carousel-container">
    <img
      :src="carouselItems[currentIndex].src"
      :alt="carouselItems[currentIndex].alt"
      class="carousel-image"
    />
    <div class="carousel-controls">
      <button @click="previous" class="carousel-control">&lt;</button>
      <div class="pagination-bar">
        <div
          v-for="(item, index) in carouselItems"
          :key="index"
          @click="goTo(index)"
          :class="{ 'pagination-item': true, active: currentIndex === index }"
        ></div>
      </div>
      <button @click="next" class="carousel-control">&gt;</button>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'ImageCarousel',
  props: {
    carouselItems: {
      type: Array<any>,
      required: true,
    },
  },
  data() {
    return {
      currentIndex: 0,
    }
  },
  methods: {
    previous() {
      this.currentIndex =
        this.currentIndex === 0
          ? this.carouselItems.length - 1
          : this.currentIndex - 1
    },
    next() {
      this.currentIndex = (this.currentIndex + 1) % this.carouselItems.length
    },
    goTo(index: number) {
      this.currentIndex = index
    },
  },
}
</script>
<style scoped lang="scss">
.carousel-container {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.carousel-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.carousel-control {
  pointer-events: auto;
  background-color: rgba(255, 255, 255, 0.5);
  border: none;
  font-size: 2rem;
  padding: 0.5rem;
  cursor: pointer;
}

.pagination-bar {
  display: flex;
  justify-content: center;
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
}

.pagination-item {
  width: 30px;
  height: 4px;
  background-color: lightgrey;
  margin-left: 2px;
  margin-right: 2px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.pagination-item.active {
  background-color: darkgrey;
}
</style>
