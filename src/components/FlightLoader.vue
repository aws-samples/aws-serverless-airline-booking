<template>
  <content-loader
    :speed="2"
    primaryColor="#861c6a"
    secondaryColor="#fa3336"
    className="flight__loader"
    ariaLabel="Loading flights..."
  >
    <rect x="23" y="23.18" rx="5" ry="5" width="55" height="4.2" />
    <rect x="23" y="29.59" rx="0" ry="0" width="78" height="37" />
    <circle
      cx="132.75393167938634"
      cy="47.343931679386344"
      r="14.753931679386344"
    />
    <rect x="23" y="68.59" rx="0" ry="0" width="76" height="3" />
    <rect x="167" y="29.59" rx="0" ry="0" width="78" height="37" />
    <rect x="187" y="23.08" rx="5" ry="5" width="57.2" height="4.3" />
    <rect x="169" y="68.59" rx="0" ry="0" width="76" height="3" />
  </content-loader>
</template>

<script>
import { ContentLoader } from 'vue-content-loader'
export default {
  /**
   *
   * Flight Loader component represents a Loading Flight state when looking up for flights in the catalog
   *
   * @example
   *
   * <flight-loader/>
   */
  components: {
    ContentLoader
  }
}
</script>
