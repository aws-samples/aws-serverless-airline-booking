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
      .add("./main.js")
      .end();
    config.resolve.alias.set("@", __dirname);
    config.resolve.alias.set(
      "variables",
      path.join(__dirname, "./styles/quasar.variables.styl")
    );
  }
};
