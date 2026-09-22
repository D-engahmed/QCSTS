"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

/** Renders the theme switch using the saved preference or system color scheme. */
export default function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem("qcsts-theme");
    const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const enabled = saved ? saved === "dark" : preferred;
    document.documentElement.classList.toggle("dark", enabled);
    setDark(enabled);
  }, []);

  /** Switches the document theme and saves the new preference. */
  function toggle() {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    window.localStorage.setItem("qcsts-theme", next ? "dark" : "light");
    setDark(next);
  }

  return (
    <button className="theme-toggle" type="button" onClick={toggle} aria-label={dark ? "Switch to light mode" : "Switch to dark mode"} title={dark ? "Light mode" : "Dark mode"}>
      {dark ? <Sun size={16} /> : <Moon size={16} />}
      <span>{dark ? "Light" : "Dark"}</span>
    </button>
  );
}
