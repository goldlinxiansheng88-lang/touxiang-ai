/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        oat: "#F5F0EB",
        blush: "#D4A5A5",
        mist: "#9CA3AF",
        /** 管理后台专用中性色，略偏暖灰 */
        admin: {
          canvas: "#ebe8e4",
          surface: "#fafaf9",
          elevated: "#ffffff",
          border: "rgba(28, 25, 23, 0.08)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        admin:
          "0 1px 2px rgba(28, 25, 23, 0.04), 0 12px 40px -8px rgba(28, 25, 23, 0.1)",
        "admin-sm": "0 1px 3px rgba(28, 25, 23, 0.06), 0 4px 12px -2px rgba(28, 25, 23, 0.08)",
        "admin-inset": "inset 0 1px 2px rgba(28, 25, 23, 0.06)",
        /** 主内容区：顶缘高光 + 软投影 */
        "admin-panel":
          "inset 0 1px 0 0 rgba(255,255,255,0.85), 0 1px 2px rgba(28,25,23,0.04), 0 24px 48px -12px rgba(28,25,23,0.12)",
      },
      backgroundImage: {
        "admin-noise":
          "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [],
};
