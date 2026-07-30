"use client";

import { useState } from "react";
import Link from "next/link";
import { supabase } from "@/config/supabase";

export default function LandingPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const { error } = await supabase
        .from("waitlist")
        .insert({ email });
      if (error) throw error;
      setSubmitted(true);
    } catch (err) {
      console.error("Failed to save email:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex-1 flex flex-col items-center justify-center px-5 py-8 sm:py-12">
      <div className="w-full max-w-xl text-center space-y-6">
        <div className="space-y-4">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold tracking-tight leading-tight text-white">
            Turn product URLs into high-converting
            {" "}
            <span className="gradient-text italic font-serif font-bold">
              video ads
            </span>{" "}
            automatically
          </h1>

          <p className="text-base sm:text-lg text-zinc-300 max-w-md mx-auto leading-relaxed">
            Extract website intelligence, generate vision-aware scripts, render AI spokespeople, and composite timed product overlays — all in seconds.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/app"
            className="w-full sm:w-auto px-8 py-4 rounded-xl bg-accent hover:bg-sky-400 text-black font-bold text-sm transition-all shadow-lg shadow-sky-500/20 cursor-pointer flex items-center justify-center gap-2 glowing-glow"
          >
            <span>Launch Pitch Demo</span>
            <span className="text-base">&rarr;</span>
          </Link>
        </div>

        {submitted ? (
          <div className="p-4 rounded-xl border border-accent/40 bg-accent/10 text-foreground text-sm glassmorphism">
            You&apos;re on the priority list. We&apos;ll be in touch shortly.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2 max-w-md mx-auto bg-zinc-950/80 p-2 rounded-2xl border border-border">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email for updates"
              className="flex-1 px-4 py-3 rounded-xl bg-transparent border-0 text-sm text-foreground placeholder:text-zinc-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-white text-sm font-semibold transition-all disabled:opacity-50 cursor-pointer"
            >
              {loading ? "..." : "Join Waitlist"}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
