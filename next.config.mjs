/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "Content-Security-Policy",
            value: "frame-src 'self' https://typebot.co https://*.typebot.co;",
          },
        ],
      },
    ]
  },
}

export default nextConfig
