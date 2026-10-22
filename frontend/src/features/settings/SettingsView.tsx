import { Settings, HardDrive, Sliders, Key } from 'lucide-react';

interface SettingsViewProps {
  userId: string;
  onUpdateUserId: (newId: string) => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ userId, onUpdateUserId }) => {
  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          <span>Studio Settings & Configuration</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Review audio engineering parameters, authentication status, and storage retention.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: User & Auth Status */}
        <div className="bg-[#121A2B] border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Key className="w-4 h-4 text-cyan-400" />
            <h3 className="font-semibold text-white text-sm">Authentication & Identity</h3>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-400 block mb-1">Active Creator ID:</span>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={userId}
                  onChange={(e) => onUpdateUserId(e.target.value)}
                  className="w-full bg-[#0B1020] border border-slate-700 rounded-xl px-3 py-2 text-slate-200 font-mono text-xs focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>

            <div className="p-3 bg-[#0B1020] rounded-xl border border-slate-800 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Mode:</span>
                <span className="text-emerald-400 font-semibold">Local Development Mode</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Firebase credentials are not configured in this environment; honest local authentication is active with full feature access.
              </p>
            </div>
          </div>
        </div>

        {/* Card 2: Audio Engineering Standards */}
        <div className="bg-[#121A2B] border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Sliders className="w-4 h-4 text-violet-400" />
            <h3 className="font-semibold text-white text-sm">Audio Engineering Standards</h3>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between items-center p-2.5 bg-[#0B1020] rounded-xl border border-slate-800">
              <span className="text-slate-400">Sample Rate</span>
              <span className="font-mono font-bold text-cyan-300">48,000 Hz (Broadcast WAV)</span>
            </div>

            <div className="flex justify-between items-center p-2.5 bg-[#0B1020] rounded-xl border border-slate-800">
              <span className="text-slate-400">Target Loudness</span>
              <span className="font-mono font-bold text-cyan-300">-16.0 LUFS (EBU R128)</span>
            </div>

            <div className="flex justify-between items-center p-2.5 bg-[#0B1020] rounded-xl border border-slate-800">
              <span className="text-slate-400">True Peak Ceiling</span>
              <span className="font-mono font-bold text-cyan-300">≤ -1.0 dBTP</span>
            </div>

            <div className="flex justify-between items-center p-2.5 bg-[#0B1020] rounded-xl border border-slate-800">
              <span className="text-slate-400">Duration Tolerance</span>
              <span className="font-mono font-bold text-emerald-400">≤ 0.05 seconds</span>
            </div>
          </div>
        </div>

        {/* Card 3: Storage & Retention */}
        <div className="bg-[#121A2B] border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4 md:col-span-2">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <HardDrive className="w-4 h-4 text-emerald-400" />
            <h3 className="font-semibold text-white text-sm">Storage & Retention Policy</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 bg-[#0B1020] rounded-xl border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Audio Storage Engine</span>
              <span className="text-white font-semibold mt-1 block">Local Persistent File Storage</span>
            </div>

            <div className="p-3 bg-[#0B1020] rounded-xl border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Database Storage</span>
              <span className="text-white font-semibold mt-1 block">Thread-Safe SQLite Engine</span>
            </div>

            <div className="p-3 bg-[#0B1020] rounded-xl border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Retention Window</span>
              <span className="text-white font-semibold mt-1 block">Unlimited in Local Dev</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
