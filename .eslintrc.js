module.exports = {
  root: true,
  extends: ['@deephaven/eslint-config'],
  parserOptions: {
    project: ['./tsconfig.eslint.json', './packages/*/tsconfig.json'],
    tsconfigRootDir: __dirname,
  },
};
