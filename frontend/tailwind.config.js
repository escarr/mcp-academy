/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  safelist: ["grid-cols-1", "md:grid-cols-2"],
  theme: {
    extend: {
      colors: {
        // Pac-Man arcade palette
        pac: "#FFFF00",       // Pac-Man yellow
        blinky: "#FF0000",    // red ghost — Tools
        pinky: "#FFB8FF",     // pink ghost — Resources
        inky: "#00FFFF",      // cyan ghost — Prompts
        clyde: "#FFB852",     // orange ghost — Transports
        maze: "#2121FF",      // maze wall blue
        pellet: "#FFB897",    // peachy pellet
        crt: "#0a0a14",       // near-black background
      },
      fontFamily: {
        arcade: ['"Press Start 2P"', "monospace"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      animation: {
        chomp: "chomp 0.35s steps(2) infinite",
        float: "float 2s ease-in-out infinite",
        flicker: "flicker 2.5s linear infinite",
        scanline: "scanline 6s linear infinite",
        "pellet-pop": "pellet-pop 0.45s ease-out",
        "ghost-bob": "ghost-bob 0.6s ease-in-out infinite",
      },
      keyframes: {
        chomp: {
          "0%, 100%": { clipPath: "polygon(0 0, 100% 0, 100% 50%, 50% 50%, 100% 50%, 100% 100%, 0 100%)" },
          "50%": { clipPath: "polygon(0 0, 100% 0, 100% 100%, 0 100%)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
        flicker: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.92" },
          "52%": { opacity: "0.6" },
          "54%": { opacity: "1" },
        },
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        "pellet-pop": {
          "0%": { transform: "scale(1)", opacity: "1" },
          "60%": { transform: "scale(2.4)", opacity: "0.4" },
          "100%": { transform: "scale(0)", opacity: "0" },
        },
        "ghost-bob": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-4px)" },
        },
      },
      boxShadow: {
        neon: "0 0 8px currentColor, 0 0 24px currentColor",
      },
    },
  },
  plugins: [],
};
