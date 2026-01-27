"use client";

import { useState } from "react";
import DiseasePage from "../components/DiseasePage";
import ProteinPage from "../components/ProteinPage";
import { BriefcaseMedical, Dna, Brain, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

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
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50 dark:from-slate-950 dark:via-blue-950/30 dark:to-indigo-950/50 font-sans text-foreground">

      {/* Hero Header */}
      <header className="flex flex-col items-center justify-center pt-32 pb-16 px-6">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 mb-4 tracking-tight text-center"
        >
          PennGene Agent
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl text-center leading-relaxed"
        >
          Your intelligent research platform for statistical genetics.
          Select a module below to get started.
        </motion.p>
      </header>

      {/* Module Cards */}
      <main className="flex-1 flex items-start justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="w-full max-w-5xl"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Module 1: Disease */}
            <button
              onClick={() => setSelectedModule('disease')}
              className="group relative flex flex-col items-center gap-6 p-8 bg-white dark:bg-slate-800 rounded-3xl shadow-xl border border-slate-100 dark:border-slate-700 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 text-center overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="z-10 flex flex-col items-center gap-4 w-full">
                <div className="w-20 h-20 rounded-2xl bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center text-blue-600 dark:text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300 shadow-sm">
                  <BriefcaseMedical size={40} />
                </div>

                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">PRS-Disease</h3>
                  <p className="text-slate-500 dark:text-slate-400">
                    Search & train Polygenic Risk Score models for diseases
                  </p>
                </div>

                <div className="mt-4 flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-medium opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
                  <span>Open Module</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </button>

            {/* Module 2: Protein */}
            <button
              onClick={() => setSelectedModule('protein')}
              className="group relative flex flex-col items-center gap-6 p-8 bg-white dark:bg-slate-800 rounded-3xl shadow-xl border border-slate-100 dark:border-slate-700 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 text-center overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="z-10 flex flex-col items-center gap-4 w-full">
                <div className="w-20 h-20 rounded-2xl bg-violet-100 dark:bg-violet-900/40 flex items-center justify-center text-violet-600 dark:text-violet-400 group-hover:bg-violet-600 group-hover:text-white transition-colors duration-300 shadow-sm">
                  <Dna size={40} />
                </div>

                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">PRS-Protein</h3>
                  <p className="text-slate-500 dark:text-slate-400">
                    Predict protein expression levels from genetic data
                  </p>
                </div>

                <div className="mt-4 flex items-center gap-2 text-violet-600 dark:text-violet-400 font-medium opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
                  <span>Open Module</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </button>

            {/* Module 3: Image */}
            <div className="relative flex flex-col items-center gap-6 p-8 bg-slate-50 dark:bg-slate-800/50 rounded-3xl border border-dashed border-slate-300 dark:border-slate-700 text-center opacity-75 cursor-not-allowed">
              <div className="absolute top-4 right-4 bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wider">
                Coming Soon
              </div>

              <div className="flex flex-col items-center gap-4 w-full">
                <div className="w-20 h-20 rounded-2xl bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-500 shadow-inner">
                  <Brain size={40} />
                </div>

                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-slate-500 dark:text-slate-400 mb-2">PRS-Image</h3>
                  <p className="text-slate-400 dark:text-slate-500">
                    Analyze image-derived phenotypes and genetic correlations
                  </p>
                </div>
              </div>
            </div>

          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-slate-400 dark:text-slate-600 text-sm">
        &copy; {new Date().getFullYear()} PennGene Team. All rights reserved.
      </footer>

    </div>
  );
}
