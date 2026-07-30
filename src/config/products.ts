export interface ProductConfig {
  id: "hermes" | "mobilerun" | "doublespeed";
  name: string;
  tagline: string;
  badge: string;
  url: string;
  description: string;
  avatar: {
    id: string;
    name: string;
    role: string;
    voiceType: string;
    thumbnail: string;
    description: string;
  };
  videoPath: string;
  summary: {
    scrapedUrl: string;
    pagesAnalyzed: number;
    visualAssetsExtracted: number;
    hookStyle: string;
    videoDuration: string;
    aspectRatio: string;
    processSteps: {
      title: string;
      description: string;
      duration: string;
      status: "completed" | "active" | "pending";
    }[];
  };
  scripts: {
    style: string;
    hook: string;
    text: string;
  }[];
}

export const PRODUCTS: Record<string, ProductConfig> = {
  hermes: {
    id: "hermes",
    name: "Hermes",
    tagline: "Autonomous Agentic Workflow Engine",
    badge: "Enterprise AI",
    url: "https://hermes-agent.nousresearch.com/",
    description: "Next-gen AI agentic framework by Nous Research that orchestrates multi-agent workflows, tool execution, and complex task pipelines.",
    avatar: {
      id: "hermes_presenter",
      name: "Jibran",
      role: "AI Lead & Tech Host",
      voiceType: "Confident & Technical",
      thumbnail: "/avatars/user_presenter.png",
      description: "Tech presenter avatar delivering high-impact multi-agent workflow & enterprise AI presentations.",
    },
    videoPath: "/api/preset-video/hermes",
    summary: {
      scrapedUrl: "https://hermes-agent.nousresearch.com/",
      pagesAnalyzed: 5,
      visualAssetsExtracted: 8,
      hookStyle: "Mind-blown Tech Discovery",
      videoDuration: "0:28",
      aspectRatio: "9:16 (Shorts / Reels / TikTok)",
      processSteps: [
        {
          title: "1. Web Intelligence Scraping",
          description: "Extracted website structure, feature breakdowns, and high-resolution DOM snapshots.",
          duration: "1.2s",
          status: "completed",
        },
        {
          title: "2. Script & Hook Generation",
          description: "Synthesized viral marketing scripts targeting enterprise AI leaders and developer teams.",
          duration: "1.8s",
          status: "completed",
        },
        {
          title: "3. Voice & Avatar Synthesis",
          description: "Generated natural neural voiceover with synchronized facial lip-sync animation.",
          duration: "3.4s",
          status: "completed",
        },
        {
          title: "4. Frame-Accurate Video Compositing",
          description: "Composited timed product screenshot overlays, animated karaoke captions, and 9:16 layout.",
          duration: "2.1s",
          status: "completed",
        },
      ],
    },
    scripts: [
      {
        style: "Viral Discovery",
        hook: "If you're still building single-prompt AI workflows, you are doing it wrong...",
        text: "If you're still building single-prompt AI workflows, you are doing it wrong. Meet Hermes: the autonomous agentic engine designed for complex multi-step workflows. Hermes coordinates autonomous sub-agents, executes code securely, and handles failures automatically. Stop debugging complex chains and experience real agentic intelligence with Hermes.",
      },
      {
        style: "Feature Deep Dive",
        hook: "Here is how enterprise engineering teams are scaling AI agents 10x faster...",
        text: "Here is how enterprise engineering teams are scaling AI agents 10x faster. Hermes automatically parses your task requirements, provisions specialized agent nodes, and routes context seamlessly across operations. Check out Hermes today to streamline your AI operations.",
      },
    ],
  },
  mobilerun: {
    id: "mobilerun",
    name: "MobileRun",
    tagline: "Autonomous Mobile App Testing Agent",
    badge: "QA Automation",
    url: "https://mobilerun.ai",
    description: "AI agent that autonomously tests mobile applications on physical iOS and Android devices with computer vision.",
    avatar: {
      id: "mobilerun_presenter",
      name: "Jibran",
      role: "Mobile Product & QA Host",
      voiceType: "Energetic & Direct",
      thumbnail: "/avatars/user_presenter.png",
      description: "Tech reviewer avatar presenting automated mobile testing workflows and developer features.",
    },
    videoPath: "/api/preset-video/mobilerun",
    summary: {
      scrapedUrl: "https://mobilerun.ai",
      pagesAnalyzed: 4,
      visualAssetsExtracted: 6,
      hookStyle: "Problem-Agitation-Solution",
      videoDuration: "0:24",
      aspectRatio: "9:16 (Shorts / Reels / TikTok)",
      processSteps: [
        {
          title: "1. Web Intelligence Scraping",
          description: "Scraped mobile testing features, live device lab specs, and visual workflow diagrams.",
          duration: "0.9s",
          status: "completed",
        },
        {
          title: "2. Script & Hook Generation",
          description: "Created high-converting hook addressing mobile QA pain points and flaky app test suites.",
          duration: "1.5s",
          status: "completed",
        },
        {
          title: "3. Voice & Avatar Synthesis",
          description: "Synthesized crisp audio voiceover and synchronized avatar presenter performance.",
          duration: "3.0s",
          status: "completed",
        },
        {
          title: "4. Frame-Accurate Video Compositing",
          description: "Overlayed mobile device UI screenshots, kinetic captions, and seamless audio track.",
          duration: "1.9s",
          status: "completed",
        },
      ],
    },
    scripts: [
      {
        style: "Problem Solver",
        hook: "Mobile app testing is broken. Flaky scripts, broken simulators, endless delays...",
        text: "Mobile app testing is broken. Flaky scripts, broken simulators, and endless manual checks slow down every deployment. MobileRun changes everything. Our AI agent runs on physical iOS and Android devices, detects visual bugs autonomously, and sends instant actionable reports right into your workflow.",
      },
      {
        style: "Product Demo Focus",
        hook: "Watch an AI agent test a full iOS checkout flow in 30 seconds...",
        text: "Watch an AI agent test a full iOS checkout flow in 30 seconds. MobileRun interacts with real device screens, verifies tap responses, and catches UI regressions before your users ever see them. Ship mobile apps faster with zero test flakiness.",
      },
    ],
  },
  doublespeed: {
    id: "doublespeed",
    name: "DoubleSpeed",
    tagline: "Autonomous Short-Form AI Video Engine",
    badge: "Viral Marketing",
    url: "https://doublespeed.ai",
    description: "Transforms any product URL into viral 9:16 short-form video ads automatically with AI avatars & overlays.",
    avatar: {
      id: "cole_avatar",
      name: "Cole",
      role: "DoubleSpeed Creator & Tech Host",
      voiceType: "Engaging & Dynamic",
      thumbnail: "/avatars/doublespeed_presenter.png",
      description: "Authentic founder avatar delivering high-converting short-form product video storytelling.",
    },
    videoPath: "/api/preset-video/doublespeed",
    summary: {
      scrapedUrl: "https://doublespeed.ai",
      pagesAnalyzed: 6,
      visualAssetsExtracted: 10,
      hookStyle: "High-Energy Brand Story",
      videoDuration: "0:30",
      aspectRatio: "9:16 (Shorts / Reels / TikTok)",
      processSteps: [
        {
          title: "1. Web Intelligence Scraping",
          description: "Crawled target website, extracted DOM tree, header messaging, and took full-page snapshots.",
          duration: "1.1s",
          status: "completed",
        },
        {
          title: "2. Script & Hook Generation",
          description: "Analyzed product value props and generated multi-angle viral marketing script options.",
          duration: "1.7s",
          status: "completed",
        },
        {
          title: "3. Voice & Avatar Synthesis",
          description: "Rendered spokesperson avatar audio and natural facial gestures matched to script timings.",
          duration: "3.2s",
          status: "completed",
        },
        {
          title: "4. Frame-Accurate Video Compositing",
          description: "Stitched dynamic website overlays, timed karaoke word captions, and rendered 1080x1920 MP4.",
          duration: "2.3s",
          status: "completed",
        },
      ],
    },
    scripts: [
      {
        style: "Viral Story",
        hook: "I turned my product URL into a high-converting video ad in under 60 seconds...",
        text: "I turned my product URL into a high-converting video ad in under 60 seconds. DoubleSpeed automatically scrapes your site, generates vision-aware scripts, renders an AI spokesperson, and composites timed screenshot overlays. No camera, no editor, no hassle.",
      },
      {
        style: "Growth Engine",
        hook: "The secret behind scaling short-form ad campaigns without a video team...",
        text: "The secret behind scaling short-form ad campaigns without a video team is complete automation. DoubleSpeed handles scraping, script generation, avatar voiceover, and FFmpeg video compositing end-to-end. Launch your next video campaign today.",
      },
    ],
  },
};
