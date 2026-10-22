import { Music, Sliders, History, FileText, Settings } from 'lucide-react';

interface NavbarProps {
  activeTab: 'studio' | 'history' | 'manifest' | 'settings';
  setActiveTab: (tab: 'studio' | 'history' | 'manifest' | 'settings') => void;
  userId: string;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, userId }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#0B1020]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setActiveTab('studio')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-cyan-400 p-[1px] shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40 transition-all">
            <div className="w-full h-full bg-[#121A2B] rounded-xl flex items-center justify-center">
              <Music className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">IncuBrix</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30">
                Music Studio
              </span>
            </div>
            <p className="text-[11px] text-slate-400">AI Background Music Engine</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <button
            onClick={() => setActiveTab('studio')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'studio'
                ? 'bg-violet-600/20 text-cyan-300 border border-violet-500/40 shadow-sm shadow-violet-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span className="hidden sm:inline">Studio</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'history'
                ? 'bg-violet-600/20 text-cyan-300 border border-violet-500/40 shadow-sm shadow-violet-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <History className="w-4 h-4" />
            <span className="hidden sm:inline">History</span>
          </button>

          <button
            onClick={() => setActiveTab('manifest')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'manifest'
                ? 'bg-violet-600/20 text-cyan-300 border border-violet-500/40 shadow-sm shadow-violet-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span className="hidden sm:inline">Manifest</span>
          </button>

          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'settings'
                ? 'bg-violet-600/20 text-cyan-300 border border-violet-500/40 shadow-sm shadow-violet-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span className="hidden sm:inline">Settings</span>
          </button>
        </nav>

        {/* User Badge */}
        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[12px] text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Local Dev Active</span>
          </div>
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center text-xs font-bold text-white shadow-md">
            {userId.substring(0, 2).toUpperCase()}
          </div>
        </div>
      </div>
    </header>
  );
};
