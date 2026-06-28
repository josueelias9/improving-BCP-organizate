import { defineConfig } from 'orval';

export default defineConfig({
  petstore: {
    input: './bcp-api.json',
    output: {
      mode: "tags-split",
      target:'./src/bcp.ts',
      client: 'fetch',
      baseUrl: 'http://localhost:8000',
  },
}
});