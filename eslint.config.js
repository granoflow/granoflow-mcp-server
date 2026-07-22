import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    ignores: ["dist/**", "coverage/**", "node_modules/**", ".local-ai/**", "scripts/**"],
  },
  {
    files: ["src/**/*.ts", "tests/**/*.ts"],
    rules: {
      "max-lines": [
        "error",
        {
          max: 600,
          skipBlankLines: false,
          skipComments: false,
        },
      ],
      "max-lines-per-function": ["error", { max: 100, skipBlankLines: false, skipComments: false }],
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
    },
  },
  {
    files: ["tests/**/*.ts"],
    rules: {
      "max-lines": [
        "error",
        {
          max: 1000,
          skipBlankLines: false,
          skipComments: false,
        },
      ],
      "max-lines-per-function": ["error", { max: 150, skipBlankLines: false, skipComments: false }],
    },
  },
);
