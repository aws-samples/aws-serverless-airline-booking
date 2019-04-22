module.exports = {
  pluginOptions: {
    quasar: {
      theme: "mat",
      importAll: true
    }
  },
  configureWebpack: {
    devtool: "source-map"
  },
  transpileDependencies: [/[\\\/]node_modules[\\\/]quasar-framework[\\\/]/]
};
