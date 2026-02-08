import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 6173,
    strictPort: true,
  },
  build: {
    outDir: 'public',  // 构建输出到 public 目录
    assetsDir: 'assets',
    // 清空 public 目录中的 assets 和 index.html，但保留 js/ 和 models/
    emptyOutDir: false,
  },
  publicDir: false,  // 禁用默认的 publicDir，因为我们自己管理
})
