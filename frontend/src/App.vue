<template>
  <router-view id="root" />
</template>

<style>
body {
  margin: 0;
  /* background-image: "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.freepik.com%2Fphotos%2Fbackground&psig=AOvVaw1BQ-496e4SMqwKvawfPVVo&ust=1639028800436000&source=images&cd=vfe&ved=0CAgQjRxqFwoTCMinwZ7A0_QCFQAAAAAdAAAAABAI"; */
}
#root {
  display: flex;
  display: -webkit-flex;
  height: 100vh;
  flex-direction: column;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  background: url("../src/assets/back3.jpg") no-repeat;
  background-size: 100% 100%;
  -webkit-background-origin: content-box; /*Safari */
  background-origin: content-box;
}
</style>