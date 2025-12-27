"use client";

import { useState } from "react";
import DiseasePage from "../components/DiseasePage";
import ProteinPage from "../components/ProteinPage";
import { BriefcaseMedical, Dna, Brain, ArrowRight } from "lucide-react";

type ModuleType = 'disease' | 'protein' | 'image' | null;

export default function Home() {
  const [selectedModule, setSelectedModule] = useState<ModuleType>(null);

  // If a module is selected, render that module's page
  if (selectedModule === 'disease') {
    return <DiseasePage onBack={() => setSelectedModule(null)} />;
  }

  if (selectedModule === 'protein') {
    return <ProteinPage onBack={() => setSelectedModule(null)} />;
  }

  // Otherwise, render the Main Selection Landing Page
  return (
    <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-slate-900 font-sans text-foreground">

      {/* Hero Header */}
      <header className="flex flex-col items-center justify-center pt-20 pb-12 px-6">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-4 tracking-tight text-center">
          PennPRS Lab
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl text-center leading-relaxed">
          Your intelligent research platform for Polygenic Risk Score analysis across diverse biological domains.
          Select a module below to begin exploring.
        </p>
      </header>

      {/* Modules Grid */}
      <main className="flex-1 flex items-center justify-center p-6 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl w-full px-4">

          {/* Module 1: Disease */}
          <button
            onClick={() => setSelectedModule('disease')}
            className="group relative flex flex-col h-[400px] p-8 bg-white dark:bg-gray-800 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 text-left overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <BriefcaseMedical size={200} />
            </div>

            <div className="z-10 flex flex-col h-full">
              <div className="w-14 h-14 mb-6 rounded-2xl bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center text-blue-600 dark:text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                <BriefcaseMedical size={32} />
              </div>

              <h3 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">PennPRS-Disease</h3>
              <div className="h-1 w-12 bg-blue-500 mb-6 rounded-full"></div>

              <p className="text-gray-500 dark:text-gray-400 text-lg mb-8 leading-relaxed">
                Search, evaluate, and train Polygenic Risk Score models for complex disease risk prediction. Leverage GWAS summary statistics and advanced statistical methods to generate clinically actionable insights.
              </p>

              <div className="mt-auto flex items-center text-blue-600 dark:text-blue-400 font-semibold group-hover:translate-x-2 transition-transform">
                Enter Module <ArrowRight className="ml-2 w-5 h-5" />
              </div>
            </div>
          </button>

          {/* Module 2: Protein */}
          <button
            onClick={() => setSelectedModule('protein')}
            className="group relative flex flex-col h-[400px] p-8 bg-white dark:bg-gray-800 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 text-left overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Dna size={200} />
            </div>

            <div className="z-10 flex flex-col h-full">
              <div className="w-14 h-14 mb-6 rounded-2xl bg-violet-100 dark:bg-violet-900/40 flex items-center justify-center text-violet-600 dark:text-violet-400 group-hover:bg-violet-600 group-hover:text-white transition-colors duration-300">
                <Dna size={32} />
              </div>

              <h3 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">PennPRS-Protein</h3>
              <div className="h-1 w-12 bg-violet-500 mb-6 rounded-full"></div>

              <p className="text-gray-500 dark:text-gray-400 text-lg mb-8 leading-relaxed">
                Predict protein expression levels and discover novel biomarkers. Explore proteomics genetic scores from OmicsPred and identify therapeutic targets.
              </p>

              <div className="mt-auto flex items-center text-violet-600 dark:text-violet-400 font-semibold group-hover:translate-x-2 transition-transform">
                Enter Module <ArrowRight className="ml-2 w-5 h-5" />
              </div>
            </div>
          </button>

          {/* Module 3: Image */}
          <div className="relative flex flex-col h-[400px] p-8 bg-gray-50 dark:bg-gray-800/50 rounded-3xl border border-dashed border-gray-300 dark:border-gray-700 text-left opacity-75 cursor-not-allowed">
            <div className="absolute top-4 right-4 bg-yellow-100 text-yellow-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
              Coming Soon
            </div>

            <div className="z-10 flex flex-col h-full grayscale-[0.5]">
              <div className="w-14 h-14 mb-6 rounded-2xl bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-500">
                <Brain size={32} />
              </div>

              <h3 className="text-3xl font-bold text-gray-500 dark:text-gray-400 mb-2">PennPRS-Image</h3>
              <div className="h-1 w-12 bg-gray-300 mb-6 rounded-full"></div>

              <p className="text-gray-500 dark:text-gray-400 text-lg mb-8 leading-relaxed">
                Predict image-derived phenotypes (IDPs) from genetic data. Analyze structural brain changes, organ morphology, and radiological biomarkers for precision medicine applications.
              </p>
            </div>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-gray-400 dark:text-gray-600 text-sm">
        &copy; {new Date().getFullYear()} PennPRS Team. All rights reserved.
      </footer>

    </div>
  );
}
