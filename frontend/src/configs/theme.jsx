

const myTheme = {
  light: {
    // ── Override built-in color tokens ─────────────────────
    colors: {
      primaryColor: "#ef4444", // Your brand purple
      lightPrimaryColor: "#f5f3ff", // Soft tint of primary
      background: "#ffffff",
      primaryContainercolor: "#ebebeb",
      secondaryContainercolor: "#faf5ff",
      textColor: "#1e1b4b",
      textSecondaryColor: "#4338ca",
      labelColor: "#3730a3",
      labelSecondaryColor: "#6d28d9",
      borderColor: "#ddd6fe",
      accent: "#7c3aed",
      accentForeground: "#ffffff",
      successColor: "#10b981",
      warningColor: "#f59e0b",
      errorColor: "#ef4444",
      infoColor: "#3b82f6",
      shadowColor: "124, 58, 237", // ← R, G, B values only (no #)
      shadowColorOpacity: "0.3",
    },

    // ── Override built-in size/spacing tokens ──────────────
    sizes: {
      radiusMd: "10px",
      fontSizeMd: "15px",
      spacingMd: "18px",
    },

    // ── Your own custom tokens (any name you want!) ────────
    custom: {
      heroBackground: "#f5f3ff",
      heroText: "#4c1d95",
      cardAccent: "#7c3aed",
      sidebarWidth: "260px",
      sidebarBg: "#faf5ff",
      chartColor1: "#7c3aed",
      chartColor2: "#2563eb",
      chartColor3: "#059669",
      navbarHeight: "64px",
      bannerGradient: "linear-gradient(135deg, #7c3aed, #2563eb)",
    },
  },

  dark: {
    // ── Dark built-in color overrides ─────────────────────
    colors: {
      primaryColor: "#a78bfa",
      lightPrimaryColor: "#2e1065",
      background: "#0f0a1e",
      primaryContainercolor: "#1e1b4b",
      secondaryContainercolor: "#12104c",
      textColor: "#f5f3ff",
      textSecondaryColor: "#c4b5fd",
      labelColor: "#ede9fe",
      labelSecondaryColor: "#a78bfa",
      borderColor: "#4c1d95",
      accent: "#a78bfa",
      accentForeground: "#0f0a1e",
      shadowColor: "167, 139, 250",
      shadowColorOpacity: "0.4",
    },

    // ── Dark custom token overrides ─────────────────────────
    // Only override what changes — anything not listed here
    // falls back to the value defined in light.custom
    custom: {
      heroBackground: "#1e1b4b",
      heroText: "#e9d5ff",
      cardAccent: "#a78bfa",
      sidebarBg: "#12104c",
      chartColor1: "#a78bfa",
      bannerGradient: "linear-gradient(135deg, #a78bfa, #60a5fa)",
    },
  },
};
export { myTheme };
