<template>
  <div id="app">
    <router-view />
  </div>
</template>
<style></style>
<script>
import { components } from "aws-amplify-vue";
export default {
  name: "app",
  components: {
    ...components
  }
};
</script>
