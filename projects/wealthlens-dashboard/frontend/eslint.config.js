import eslint from '@eslint/js'
import typescriptEslint from 'typescript-eslint'
import eslintPluginVue from 'eslint-plugin-vue'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'
import globals from 'globals'

export default typescriptEslint.config(
  { ignores: ['node_modules', 'dist'] },
  {
    extends: [
      eslint.configs.recommended,
      ...typescriptEslint.configs.recommended,
      ...eslintPluginVue.configs['flat/recommended'],
    ],
    files: ['**/*.{ts,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: globals.browser,
      parserOptions: {
        parser: typescriptEslint.parser,
      },
    },
    rules: {
      // Allow single-word component names (e.g. App.vue)
      'vue/multi-word-component-names': 'off',
    },
  },
  skipFormatting,
)
