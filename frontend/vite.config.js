import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': './src', // Esto asegura que "@" apunte a la carpeta "src"
    },
  },
  server: {
    port: 5173, // Verifica el puerto si estás usando otro
    open: true,  // Para abrir la app automáticamente al iniciar
  },
  base: '/',  // Verifica que esté configurado correctamente para tu ruta base
});
