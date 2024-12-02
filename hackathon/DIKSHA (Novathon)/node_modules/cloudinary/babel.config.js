const presets = [
  [
    [
      "env",
      {
        targets: { node: "4" }
      }
    ],
    "stage-0"
  ]
];
const plugins = ["transform-object-rest-spread"];

module.exports = { presets, plugins };
