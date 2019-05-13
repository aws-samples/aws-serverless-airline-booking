const path = require("path");

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
  transpileDependencies: [/[\\\/]node_modules[\\\/]quasar-framework[\\\/]/],
  chainWebpack: config => {
    config
      .entry("app")
      .clear()
      .add("./src/frontend/main.js")
      .end();
    config.resolve.alias.set("@", path.join(__dirname, "./src/frontend"));
    config.resolve.alias.set(
      "variables",
      path.join(__dirname, "./src/frontend/styles/quasar.variables.styl")
    );
  }
};
