"use client";

import { useState, useEffect, useRef } from "react";
import { PRODUCTS, ProductConfig } from "@/config/products";

type DemoStep = "select_product" | "avatar_preview" | "creating_ad" | "showcase";

export default function PitchDemoPage() {
  const [step, setStep] = useState<DemoStep>("select_product");
  const [selectedProductKey, setSelectedProductKey] = useState<string>("doublespeed");
  const [loadingProgress, setLoadingProgress] = useState<number>(0);
  const [currentLoadingMessage, setCurrentLoadingMessage] = useState<string>("");
  const [activeStepIndex, setActiveStepIndex] = useState<number>(0);

  const selectedProduct: ProductConfig = PRODUCTS[selectedProductKey] || PRODUCTS.doublespeed;

  // Handle animated progress when in "creating_ad" step
  useEffect(() => {
    if (step !== "creating_ad") return;

    setLoadingProgress(5);
    setActiveStepIndex(0);
    setCurrentLoadingMessage("Extracting product DOM tree and visual assets...");

    const intervals: NodeJS.Timeout[] = [];

    intervals.push(
      setTimeout(() => {
        setLoadingProgress(28);
        setActiveStepIndex(0);
        setCurrentLoadingMessage("Web Intelligence Scraping complete. Captured snapshots.");
      }, 900)
    );

    intervals.push(
      setTimeout(() => {
        setLoadingProgress(55);
        setActiveStepIndex(1);
        setCurrentLoadingMessage("Synthesizing vision script and marketing hooks...");
      }, 2100)
    );

    intervals.push(
      setTimeout(() => {
        setLoadingProgress(80);
        setActiveStepIndex(2);
        setCurrentLoadingMessage("Generating avatar speech and neural lip-sync audio...");
      }, 3400)
    );

    intervals.push(
      setTimeout(() => {
        setLoadingProgress(96);
        setActiveStepIndex(3);
        setCurrentLoadingMessage("FFmpeg compositing screenshot overlays and karaoke captions...");
      }, 4700)
    );

    intervals.push(
      setTimeout(() => {
        setLoadingProgress(100);
        setStep("showcase");
      }, 5800)
    );

    return () => {
      intervals.forEach((t) => clearTimeout(t));
    };
  }, [step]);

  return (
    <main className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-8 sm:py-12 w-full max-w-5xl mx-auto">
      {/* Header Badge */}
      <header className="mb-8 text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-sky-500/30 bg-sky-500/10 text-xs font-mono text-sky-300 tracking-wide">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          Autonomous Video Creation Engine — Demo Pitch
        </div>
      </header>

      {/* Step Stepper */}
      <Stepper current={step} />

      {/* Step 1: Select Product */}
      {step === "select_product" && (
        <SelectProductStep
          selectedKey={selectedProductKey}
          onSelectProduct={(key) => setSelectedProductKey(key)}
          onNext={() => setStep("avatar_preview")}
        />
      )}

      {/* Step 2: Avatar Preview */}
      {step === "avatar_preview" && (
        <AvatarPreviewStep
          product={selectedProduct}
          onBack={() => setStep("select_product")}
          onGenerate={() => setStep("creating_ad")}
        />
      )}

      {/* Step 3: Creating Ad Loading Screen */}
      {step === "creating_ad" && (
        <CreatingAdStep
          product={selectedProduct}
          progress={loadingProgress}
          message={currentLoadingMessage}
          activeIndex={activeStepIndex}
        />
      )}

      {/* Step 4: Final Showcase & Summary */}
      {step === "showcase" && (
        <ShowcaseStep
          product={selectedProduct}
          onRestart={() => setStep("select_product")}
        />
      )}
    </main>
  );
}

/* ─── Stepper Component ─── */

function Stepper({ current }: { current: DemoStep }) {
  const steps: { key: DemoStep; label: string; name: string }[] = [
    { key: "select_product", label: "01", name: "Choose Product" },
    { key: "avatar_preview", label: "02", name: "Presenter Avatar" },
    { key: "creating_ad", label: "03", name: "Creating Ad Post" },
    { key: "showcase", label: "04", name: "Ad Post & Summary" },
  ];

  const currentIdx = steps.findIndex((s) => s.key === current);

  return (
    <nav aria-label="Demo progress" className="w-full max-w-2xl mb-10 px-2">
      <div className="flex items-center justify-between">
        {steps.map((s, i) => {
          const isActive = i === currentIdx;
          const isCompleted = i < currentIdx;

          return (
            <div key={s.key} className="flex items-center gap-2">
              <div className="flex flex-col items-center gap-1.5">
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center text-xs font-mono font-bold transition-all duration-300 ${
                    isCompleted
                      ? "bg-accent text-black shadow-md shadow-accent/20"
                      : isActive
                        ? "bg-gradient-to-r from-sky-500 to-indigo-500 text-white ring-4 ring-sky-500/20"
                        : "border border-border bg-card/50 text-zinc-500"
                  }`}
                >
                  {isCompleted ? "✓" : s.label}
                </div>
                <span
                  className={`text-[11px] font-medium tracking-tight hidden sm:block ${
                    isActive
                      ? "text-sky-400 font-semibold"
                      : isCompleted
                        ? "text-zinc-300"
                        : "text-zinc-500"
                  }`}
                >
                  {s.name}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`w-8 sm:w-16 h-[2px] transition-colors duration-500 mb-5 sm:mb-6 ${
                    i < currentIdx ? "bg-accent" : "bg-zinc-800"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </nav>
  );
}

/* ─── Step 1: Select Product ─── */

function SelectProductStep({
  selectedKey,
  onSelectProduct,
  onNext,
}: {
  selectedKey: string;
  onSelectProduct: (key: string) => void;
  onNext: () => void;
}) {
  return (
    <div className="w-full max-w-3xl space-y-8 animate-fadeIn">
      <div className="text-center space-y-3">
        <h1 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-white">
          Choose Target Product
        </h1>
        <p className="text-sm sm:text-base text-zinc-400 max-w-lg mx-auto leading-relaxed">
          Select a product showcase to initiate automated web scraping, script synthesis, and 9:16 ad video generation.
        </p>
      </div>

      {/* 3 Product Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {Object.values(PRODUCTS).map((prod) => {
          const isSelected = selectedKey === prod.id;
          return (
            <div
              key={prod.id}
              onClick={() => onSelectProduct(prod.id)}
              className={`group relative p-6 rounded-2xl border transition-all duration-300 cursor-pointer text-left flex flex-col justify-between ${
                isSelected
                  ? "border-accent ring-2 ring-accent/40 bg-card/90 glowing-glow"
                  : "border-border/80 bg-card/40 hover:border-zinc-500 hover:bg-card/70"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-zinc-800/80 border border-zinc-700/80 text-zinc-300 uppercase tracking-wider">
                    {prod.badge}
                  </span>
                  <div
                    className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                      isSelected
                        ? "border-accent bg-accent"
                        : "border-zinc-600 group-hover:border-zinc-400"
                    }`}
                  >
                    {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-black" />}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-serif font-bold text-white group-hover:text-accent transition-colors">
                    {prod.name}
                  </h3>
                  <p className="text-xs text-sky-400 font-mono mt-0.5">{prod.url}</p>
                </div>

                <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">
                  {prod.description}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-zinc-800/60 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                <span>Presenter: <strong className="text-zinc-300">{prod.avatar.name}</strong></span>
                <span className="text-accent group-hover:translate-x-1 transition-transform">Select &rarr;</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Greyed Out Custom Link Option */}
      <div className="max-w-md mx-auto p-4 rounded-2xl border border-zinc-800/60 bg-zinc-950/40 opacity-60 cursor-not-allowed">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-mono text-zinc-400">Or enter custom product URL</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 uppercase">
            Coming Soon (Pitch Demo)
          </span>
        </div>
        <div className="flex gap-2">
          <input
            type="url"
            disabled
            placeholder="https://your-custom-product.com"
            className="flex-1 px-3.5 py-2.5 rounded-xl bg-zinc-900/50 border border-zinc-800 text-xs text-zinc-500 placeholder:text-zinc-600 cursor-not-allowed focus:outline-none"
          />
          <button
            disabled
            className="px-4 py-2.5 rounded-xl bg-zinc-800 text-zinc-500 text-xs font-semibold cursor-not-allowed"
          >
            Submit
          </button>
        </div>
      </div>

      {/* Action Bar */}
      <div className="flex justify-center pt-2">
        <button
          onClick={onNext}
          className="px-8 py-4 rounded-xl bg-accent hover:bg-sky-400 text-black text-sm font-bold tracking-wide transition-all shadow-lg shadow-sky-500/20 cursor-pointer flex items-center gap-2"
        >
          <span>Continue to Presenter Selection</span>
          <span className="text-base">&rarr;</span>
        </button>
      </div>
    </div>
  );
}

/* ─── Step 2: Avatar Preview ─── */

function AvatarPreviewStep({
  product,
  onBack,
  onGenerate,
}: {
  product: ProductConfig;
  onBack: () => void;
  onGenerate: () => void;
}) {
  const avatar = product.avatar;

  return (
    <div className="w-full max-w-2xl space-y-8 animate-fadeIn">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-serif font-bold text-white">
          Brand Presenter Avatar
        </h2>
        <p className="text-sm text-zinc-400">
          Available AI presenter assigned to generate the video post for{" "}
          <span className="text-sky-400 font-semibold">{product.name}</span>
        </p>
      </div>

      {/* Avatar Detail Card */}
      <div className="p-6 sm:p-8 rounded-3xl border border-accent/40 bg-card/80 glassmorphism glowing-glow space-y-6">
        <div className="flex flex-col sm:flex-row gap-6 items-center sm:items-start">
          {/* Avatar Thumbnail Box */}
          <div className="w-32 h-40 rounded-2xl overflow-hidden bg-zinc-800/80 border border-zinc-700/80 relative shrink-0">
            <img
              src={avatar.thumbnail}
              alt={avatar.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                // Fallback styled avatar placeholder if image is missing
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-t from-black/80 via-transparent to-transparent">
              <span className="text-3xl">👤</span>
            </div>
            <div className="absolute bottom-2 left-2 right-2 px-2 py-0.5 rounded bg-black/60 backdrop-blur-md text-[10px] font-mono text-sky-300 text-center">
              AI Presenter
            </div>
          </div>

          {/* Details */}
          <div className="space-y-4 text-center sm:text-left flex-1">
            <div>
              <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-md bg-accent/10 border border-accent/30 text-accent text-xs font-mono mb-2">
                Available for {product.name}
              </div>
              <h3 className="text-2xl font-serif font-bold text-white">{avatar.name}</h3>
              <p className="text-xs text-sky-400 font-mono">{avatar.role}</p>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              {avatar.description}
            </p>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800">
                <span className="text-[10px] font-mono uppercase text-zinc-500 block">Voice Delivery</span>
                <span className="text-xs font-semibold text-zinc-200">{avatar.voiceType}</span>
              </div>
              <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800">
                <span className="text-[10px] font-mono uppercase text-zinc-500 block">Target Format</span>
                <span className="text-xs font-semibold text-zinc-200">9:16 Vertical Video</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={onBack}
          className="px-5 py-3 rounded-xl border border-zinc-800 text-xs font-mono text-zinc-400 hover:text-white hover:border-zinc-600 transition-colors"
        >
          &larr; Change Product
        </button>

        <button
          onClick={onGenerate}
          className="px-8 py-4 rounded-xl bg-accent hover:bg-sky-400 text-black text-sm font-bold transition-all shadow-lg shadow-sky-500/20 cursor-pointer flex items-center gap-2"
        >
          <span>Generate Product Ad Post</span>
          <span className="text-base">🎬</span>
        </button>
      </div>
    </div>
  );
}

/* ─── Step 3: Creating Ad Post Loading Screen ─── */

function CreatingAdStep({
  product,
  progress,
  message,
  activeIndex,
}: {
  product: ProductConfig;
  progress: number;
  message: string;
  activeIndex: number;
}) {
  const steps = [
    {
      title: "1. Web Intelligence Scraping",
      desc: "Extracting website DOM structure, header metadata, & screenshot frames",
    },
    {
      title: "2. Script & Hook Synthesis",
      desc: "Drafting high-converting vision-aware script and viral hooks",
    },
    {
      title: "3. Voice & Avatar Synthesis",
      desc: "Generating neural audio voiceover & sync avatar video frames",
    },
    {
      title: "4. Frame-Accurate Video Compositing",
      desc: "Stitching dynamic overlays, karaoke captions, & rendering 9:16 MP4",
    },
  ];

  return (
    <div className="w-full max-w-xl text-center space-y-8 animate-fadeIn">
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/30 text-accent text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-accent animate-ping" />
          Processing Product: {product.name}
        </div>
        <h2 className="text-3xl font-serif font-bold text-white">
          Creating Product Ad Post
        </h2>
        <p className="text-sm text-zinc-400">
          Running autonomous video pipeline for <span className="text-sky-400 font-mono">{product.url}</span>
        </p>
      </div>

      {/* Main Progress Ring / Bar */}
      <div className="p-6 rounded-2xl border border-border bg-card/60 space-y-4 glassmorphism">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-zinc-300 truncate max-w-[320px] text-left">{message}</span>
          <span className="text-accent font-bold text-base font-mono">{progress}%</span>
        </div>

        <div className="h-3 w-full rounded-full bg-zinc-900 border border-zinc-800 overflow-hidden p-[1px]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-accent via-indigo-400 to-purple-500 transition-all duration-700 glowing-glow"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Step Checklist Timeline */}
      <div className="space-y-3 text-left">
        {steps.map((s, idx) => {
          const isDone = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          return (
            <div
              key={idx}
              className={`p-4 rounded-xl border transition-all duration-300 flex items-start gap-4 ${
                isDone
                  ? "border-emerald-500/30 bg-emerald-500/5 text-zinc-300"
                  : isCurrent
                    ? "border-accent bg-accent/10 text-white glowing-glow"
                    : "border-zinc-800/60 bg-zinc-950/40 text-zinc-500"
              }`}
            >
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0 mt-0.5 ${
                  isDone
                    ? "bg-emerald-500 text-black"
                    : isCurrent
                      ? "bg-accent text-black animate-pulse"
                      : "border border-zinc-700 text-zinc-600"
                }`}
              >
                {isDone ? "✓" : idx + 1}
              </div>

              <div className="space-y-0.5">
                <h4
                  className={`text-sm font-semibold ${
                    isCurrent ? "text-accent" : isDone ? "text-zinc-200" : "text-zinc-500"
                  }`}
                >
                  {s.title}
                </h4>
                <p className="text-xs text-zinc-400 leading-snug">{s.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── Step 4: Final Showcase & Pipeline Summary ─── */

function ShowcaseStep({
  product,
  onRestart,
}: {
  product: ProductConfig;
  onRestart: () => void;
}) {
  const [activeScriptTab, setActiveScriptTab] = useState<number>(0);
  const [copied, setCopied] = useState<boolean>(false);
  const [videoError, setVideoError] = useState<boolean>(false);
  const [showLaunchModal, setShowLaunchModal] = useState<boolean>(false);

  const currentScript = product.scripts[activeScriptTab] || product.scripts[0];

  function handleCopyScript() {
    if (!currentScript) return;
    navigator.clipboard.writeText(currentScript.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="w-full max-w-5xl space-y-8 animate-fadeIn relative">
      {/* Elegant Launch Confirmation Modal */}
      {showLaunchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-md rounded-2xl border border-sky-500/40 bg-zinc-950 p-6 shadow-2xl space-y-6 text-center glowing-glow relative overflow-hidden">
            {/* Top glowing accent bar */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-sky-400 via-indigo-500 to-emerald-400" />
            
            {/* Icon */}
            <div className="mx-auto w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-3xl animate-bounce">
              🚀
            </div>

            <div className="space-y-2">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold">
                ✓ Campaign Live &amp; Published
              </div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Campaign Launched!
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Your video ad post for <span className="text-sky-300 font-semibold">{product.name}</span> has been queued &amp; deployed across target social automation channels.
              </p>
            </div>

            {/* Platform status cards */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-4 text-left space-y-2.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-300 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  Social Automation Routing
                </span>
                <span className="font-mono text-emerald-400 text-[11px] font-bold">Active</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-300 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-sky-400" />
                  Target Platforms (X/TikTok/Reels)
                </span>
                <span className="font-mono text-sky-400 text-[11px] font-bold">Synced</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-300 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-purple-400" />
                  Performance Analytics
                </span>
                <span className="font-mono text-purple-400 text-[11px] font-bold">Enabled</span>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-2 flex gap-3">
              <button
                onClick={() => setShowLaunchModal(false)}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-accent via-sky-400 to-indigo-500 hover:brightness-110 text-black font-bold text-xs tracking-wide shadow-lg shadow-sky-500/20 transition-all cursor-pointer"
              >
                Done &amp; Close
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
          ✓ Ad Post Generated Successfully
        </div>
        <h2 className="text-3xl font-serif font-bold text-white">
          Product Ad Campaign Ready
        </h2>
        <p className="text-sm text-zinc-400">
          Generated ad video post for{" "}
          <span className="text-sky-400 font-semibold">{product.name}</span> alongside automated build summary
        </p>
      </div>

      {/* Main Grid: Left Video Player, Right "How It Was Made" Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: 9:16 Video Player Container */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative aspect-[9/16] rounded-2xl overflow-hidden border border-accent/40 bg-black shadow-2xl glowing-glow">
            {!videoError ? (
              <video
                src={product.videoPath}
                controls
                autoPlay
                loop
                playsInline
                onError={() => setVideoError(true)}
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center space-y-3 bg-zinc-900">
                <span className="text-4xl">🎬</span>
                <p className="text-xs font-mono text-zinc-300">
                  Video Stream Ready ({product.name})
                </p>
                <p className="text-[11px] text-zinc-500">
                  Video file path: {product.videoPath}
                </p>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <button
              onClick={onRestart}
              className="flex-1 px-4 py-3 rounded-xl border border-zinc-800 hover:border-zinc-600 bg-card/40 text-xs font-mono text-zinc-300 transition-colors cursor-pointer"
            >
              🔄 Choose Another Product
            </button>
            <button
              onClick={() => setShowLaunchModal(true)}
              className="flex-1 px-4 py-3 rounded-xl bg-accent hover:bg-sky-400 text-black text-xs font-bold transition-all shadow-md shadow-sky-500/20 cursor-pointer"
            >
              🚀 Launch Campaign
            </button>
          </div>
        </div>

        {/* Right Column: "How It Was Made" Summary */}
        <div className="lg:col-span-7 space-y-6">
          {/* Summary Card */}
          <div className="rounded-2xl border border-border bg-card/70 p-6 space-y-6 glassmorphism">
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
              <div>
                <h3 className="text-lg font-serif font-bold text-white flex items-center gap-2">
                  <span>⚡</span> How It Was Made
                </h3>
                <p className="text-xs text-zinc-400 font-mono mt-0.5">
                  High-level process breakdown &amp; execution summary
                </p>
              </div>
              <span className="text-[10px] font-mono px-2.5 py-1 rounded bg-sky-500/10 border border-sky-500/30 text-sky-300">
                Full Process
              </span>
            </div>

            {/* Pipeline Process Steps Summary */}
            <div className="space-y-3">
              {product.summary.processSteps.map((step, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80 flex items-start justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <h4 className="font-semibold text-zinc-200">{step.title}</h4>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                  <span className="text-[10px] font-mono text-accent bg-accent/10 px-2 py-0.5 rounded shrink-0">
                    {step.duration}
                  </span>
                </div>
              ))}
            </div>

            {/* High-Level Pipeline Specs Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800">
                <span className="text-[10px] font-mono text-zinc-500 block uppercase">Pages Analyzed</span>
                <span className="text-xs font-bold text-white">{product.summary.pagesAnalyzed} Pages</span>
              </div>
              <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800">
                <span className="text-[10px] font-mono text-zinc-500 block uppercase">Visual Assets</span>
                <span className="text-xs font-bold text-white">{product.summary.visualAssetsExtracted} Extracted</span>
              </div>
              <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 col-span-2 sm:col-span-1">
                <span className="text-[10px] font-mono text-zinc-500 block uppercase">Format & Ratio</span>
                <span className="text-xs font-bold text-white">9:16 Vertical</span>
              </div>
            </div>
          </div>

          {/* Generated Scripts Breakdown Card */}
          <div className="rounded-2xl border border-border bg-card/70 p-6 space-y-4 glassmorphism">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-serif font-bold text-white">Generated Voiceover Script</h3>
                <p className="text-xs text-zinc-400 font-mono">Synthesized for target ad video</p>
              </div>
              <button
                onClick={handleCopyScript}
                className="px-3 py-1.5 rounded-lg border border-accent/40 bg-accent/10 hover:bg-accent/20 text-accent text-xs font-mono transition-all flex items-center gap-1"
              >
                {copied ? "✓ Copied" : "📋 Copy Script"}
              </button>
            </div>

            {/* Script Tabs */}
            {product.scripts.length > 1 && (
              <div className="flex gap-2 border-b border-zinc-800 pb-2">
                {product.scripts.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveScriptTab(idx)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all capitalize ${
                      activeScriptTab === idx
                        ? "bg-accent text-black font-bold"
                        : "bg-zinc-800/60 text-zinc-400 hover:text-white"
                    }`}
                  >
                    {s.style}
                  </button>
                ))}
              </div>
            )}

            {/* Script Content */}
            {currentScript && (
              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-zinc-900/80 border border-zinc-800/80">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-accent font-bold block mb-1">
                    Opening Hook:
                  </span>
                  <p className="text-xs text-zinc-200 font-serif italic">
                    &quot;{currentScript.hook}&quot;
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/80">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-bold block mb-1.5">
                    Voiceover Script Text:
                  </span>
                  <p className="text-xs text-zinc-300 leading-relaxed font-sans whitespace-pre-wrap">
                    {currentScript.text}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
