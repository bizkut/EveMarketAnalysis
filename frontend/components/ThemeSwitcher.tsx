"use client";

import * as React from "react";
import { useTheme } from "next-themes";

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  return (
    <button
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
      className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600"
    >
      {theme === "light" ? "Dark" : "Light"} Mode
    </button>
  );
}