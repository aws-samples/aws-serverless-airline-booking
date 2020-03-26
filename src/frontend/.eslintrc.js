module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: ["plugin:vue/essential", "@vue/prettier"],
  rules: {
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
    "no-console": "off"
  },
  parserOptions: {
    parser: "babel-eslint"
  }
};
