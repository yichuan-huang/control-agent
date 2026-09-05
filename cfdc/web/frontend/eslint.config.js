import tseslint from "typescript-eslint";
export default tseslint.config(
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      "src/api/schema.d.ts",
      "playwright-report/**",
      "test-results/**",
    ],
  },
  ...tseslint.configs.recommended,
);
