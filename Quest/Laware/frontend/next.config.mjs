/** @type {import('next').NextConfig} */
const nextConfig = {
    webpack: (config) => {
      config.resolve.alias.canvas = false;
  
      return config;
    },
  };
  
  export default nextConfig;
  