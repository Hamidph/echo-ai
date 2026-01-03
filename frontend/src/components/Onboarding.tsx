"use client";

import { useState, useEffect } from "react";
import Card from "./ui/Card";
import Button from "./ui/Button";

interface OnboardingStep {
  title: string;
  description: string;
  target?: string;
  position?: "top" | "bottom" | "left" | "right";
}

const onboardingSteps: OnboardingStep[] = [
  {
    title: "Welcome to Echo AI! 🎉",
    description:
      "Let's take a quick tour to help you get started with AI search analytics. This will only take a minute.",
  },
  {
    title: "Understanding Visibility",
    description:
      "Visibility shows how often your brand appears in AI responses. Higher visibility means more exposure to potential customers.",
    target: "visibility-metric",
  },
  {
    title: "Track Your Position",
    description:
      "Position indicates where your brand ranks among competitors in AI search results. Lower numbers mean better placement.",
    target: "position-metric",
  },
  {
    title: "Monitor Sentiment",
    description:
      "Sentiment measures how AI platforms describe your brand. Scores range from 0-100, with higher being better.",
    target: "sentiment-metric",
  },
  {
    title: "Create Your First Experiment",
    description:
      "Run experiments to test how AI platforms respond to different prompts about your brand. Each experiment provides statistical insights.",
    target: "create-experiment-button",
  },
  {
    title: "You're All Set! 🚀",
    description:
      "You're ready to start analyzing your brand's AI visibility. Run your first experiment to get started!",
  },
];

interface OnboardingProps {
  onComplete: () => void;
}

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  const step = onboardingSteps[currentStep];
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === onboardingSteps.length - 1;

  useEffect(() => {
    // Check if user has completed onboarding
    const completed = localStorage.getItem("onboarding_completed");
    if (completed) {
      setIsVisible(false);
    }
  }, []);

  const handleNext = () => {
    if (isLastStep) {
      completeOnboarding();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    completeOnboarding();
  };

  const completeOnboarding = () => {
    localStorage.setItem("onboarding_completed", "true");
    setIsVisible(false);
    onComplete();
  };

  if (!isVisible) return null;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" />

      {/* Onboarding Card */}
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md px-4">
        <Card variant="glass" padding="lg" className="shadow-2xl">
          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">
                Step {currentStep + 1} of {onboardingSteps.length}
              </span>
              <button
                onClick={handleSkip}
                className="text-sm text-gray-400 hover:text-white transition"
              >
                Skip tour
              </button>
            </div>
            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all duration-300"
                style={{
                  width: `${((currentStep + 1) / onboardingSteps.length) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Content */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-3">{step.title}</h2>
            <p className="text-gray-300 leading-relaxed">{step.description}</p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between gap-3">
            <Button
              variant="ghost"
              onClick={handlePrevious}
              disabled={isFirstStep}
              className={isFirstStep ? "invisible" : ""}
            >
              ← Previous
            </Button>
            <div className="flex gap-1.5">
              {onboardingSteps.map((_, index) => (
                <div
                  key={index}
                  className={`h-2 rounded-full transition-all ${
                    index === currentStep
                      ? "w-8 bg-gradient-to-r from-cyan-500 to-violet-500"
                      : index < currentStep
                      ? "w-2 bg-cyan-500/50"
                      : "w-2 bg-white/10"
                  }`}
                />
              ))}
            </div>
            <Button variant="primary" onClick={handleNext}>
              {isLastStep ? "Get Started" : "Next →"}
            </Button>
          </div>
        </Card>
      </div>
    </>
  );
}

// Helper component to mark elements as onboarding targets
export function OnboardingTarget({
  id,
  children,
}: {
  id: string;
  children: React.ReactNode;
}) {
  return (
    <div data-onboarding-target={id} className="relative">
      {children}
    </div>
  );
}

// Quick help tooltips for key metrics
export function MetricExplainer({ metric }: { metric: "visibility" | "position" | "sentiment" }) {
  const explanations = {
    visibility: {
      title: "What is Visibility?",
      description:
        "Visibility measures the percentage of AI responses that mention your brand. Higher visibility means your brand appears more frequently in relevant conversations.",
      example: "72% visibility means your brand appears in 72 out of 100 relevant AI responses.",
    },
    position: {
      title: "What is Position?",
      description:
        "Position indicates where your brand ranks among competitors when mentioned. Lower numbers (closer to #1) indicate better placement.",
      example: "Position #2 means your brand is typically mentioned second among competitors.",
    },
    sentiment: {
      title: "What is Sentiment?",
      description:
        "Sentiment scores how positively or negatively AI platforms describe your brand, on a scale from 0-100. Higher scores indicate more favorable mentions.",
      example: "A sentiment score of 94 means AI responses about your brand are highly positive.",
    },
  };

  const info = explanations[metric];

  return (
    <div className="p-4 bg-white/5 border border-white/10 rounded-xl">
      <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
        <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {info.title}
      </h4>
      <p className="text-xs text-gray-400 mb-2">{info.description}</p>
      <div className="p-2 bg-cyan-500/5 border border-cyan-500/20 rounded text-xs text-cyan-300">
        💡 {info.example}
      </div>
    </div>
  );
}
