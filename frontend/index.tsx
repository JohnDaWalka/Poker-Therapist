
import React, { useState, useEffect, useMemo, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { GoogleGenAI, Modality, Type } from "@google/genai";
import { 
  PlusCircle, 
  History, 
  TrendingUp, 
  BrainCircuit, 
  DollarSign, 
  Clock, 
  Target,
  Trash2,
  MessageSquare,
  BarChart3,
  Image as ImageIcon,
  Video as VideoIcon,
  Mic,
  MicOff,
  Search,
  MapPin,
  Sparkles,
  RefreshCw,
  Download,
  Upload,
  Layers,
  ChevronRight,
  Filter,
  ArrowUpDown,
  Bold,
  Italic,
  Type as TypeIcon,
  CircleAlert,
  Tag as TagIcon,
  X,
  ChevronDown,
  ExternalLink,
  Notebook,
  Music,
  Save,
  Clock3,
  Calculator,
  UserCircle,
  Play,
  Square,
  Pause,
  FolderOpen,
  Hash,
  Dice5,
  SortAsc,
  SortDesc,
  Eye,
  Percent,
  Coins
} from 'lucide-react';
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

// --- Types ---
interface LabHistoryItem {
  id: string;
  timestamp: string;
  prompt: string;
  response: string;
  strategicTags?: string[];
  sizingAdvice?: string;
  media?: { data: string, type: string };
}

interface SessionMedia {
  id: string;
  data: string;
  type: string;
  category: 'Hand Screenshot' | 'Table View' | 'Player Cam' | 'Audio Note';
}

interface Session {
  id: string;
  date: string;
  stakes: string;
  location: string;
  duration: number;
  profit: number;
  tags: string[];
  notes?: string;
  mediaItems: SessionMedia[];
}

interface ActiveSession {
  startTime: number;
  location: string;
  stakes: string;
  currentProfit: number;
  isPaused: boolean;
  pauseStart?: number;
  totalPausedTime: number;
}

type SortField = 'date' | 'profit' | 'stakes';
type LabSortField = 'timestamp' | 'prompt';
type SortOrder = 'asc' | 'desc';
type MediaCategory = SessionMedia['category'] | 'All';

// --- Utils ---
const blobToBase64 = (blob: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = (reader.result as string).split(',')[1];
      resolve(base64String);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

// --- App Component ---
const PokerApp = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'sessions' | 'lab' | 'live' | 'creative'>('dashboard');
  
  const [activeSession, setActiveSession] = useState<ActiveSession | null>(null);
  const [sessionTimer, setSessionTimer] = useState(0);

  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [expandedSessionId, setExpandedSessionId] = useState<string | null>(null);
  const [mediaFilter, setMediaFilter] = useState<MediaCategory>('All');

  const [labHistory, setLabHistory] = useState<LabHistoryItem[]>([]);
  const [showLabHistory, setShowLabHistory] = useState(false);
  const [labSortField, setLabSortField] = useState<LabSortField>('timestamp');
  const [labSortOrder, setLabSortOrder] = useState<SortOrder>('desc');

  const [newSession, setNewSession] = useState<Partial<Session>>({
    date: new Date().toISOString().split('T')[0],
    stakes: '1/2 NL',
    location: 'Local Casino',
    duration: 4,
    profit: 0,
    tags: []
  });

  const [labPrompt, setLabPrompt] = useState('');
  const [labMedia, setLabMedia] = useState<{data: string, type: string} | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const [labStrategicTags, setLabStrategicTags] = useState<string[]>([]);
  const [labSizingAdvice, setLabSizingAdvice] = useState<string | null>(null);
  
  // Sizing Calculator State
  const [potSize, setPotSize] = useState<string>('100');
  const [customSizing, setCustomSizing] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('poker_sessions_v6');
    if (saved) setSessions(JSON.parse(saved));
    const savedLab = localStorage.getItem('lab_history_v3');
    if (savedLab) setLabHistory(JSON.parse(savedLab));
    const savedActive = localStorage.getItem('active_session_v1');
    if (savedActive) setActiveSession(JSON.parse(savedActive));
  }, []);

  useEffect(() => {
    localStorage.setItem('poker_sessions_v6', JSON.stringify(sessions));
  }, [sessions]);

  useEffect(() => {
    localStorage.setItem('lab_history_v3', JSON.stringify(labHistory));
  }, [labHistory]);

  useEffect(() => {
    if (activeSession) {
      localStorage.setItem('active_session_v1', JSON.stringify(activeSession));
    } else {
      localStorage.removeItem('active_session_v1');
    }
  }, [activeSession]);

  useEffect(() => {
    let interval: number;
    if (activeSession && !activeSession.isPaused) {
      interval = window.setInterval(() => {
        const now = Date.now();
        const elapsed = (now - activeSession.startTime - activeSession.totalPausedTime) / 1000;
        setSessionTimer(elapsed);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeSession]);

  const stats = useMemo(() => {
    const totalProfit = sessions.reduce((acc, s) => acc + s.profit, 0);
    const totalHours = sessions.reduce((acc, s) => acc + s.duration, 0);
    const hourlyRate = totalHours > 0 ? totalProfit / totalHours : 0;
    const winRate = sessions.length > 0 ? (sessions.filter(s => s.profit > 0).length / sessions.length) * 100 : 0;
    let runningTotal = 0;
    const sortedForChart = [...sessions].sort((a, b) => a.date.localeCompare(b.date));
    const chartData = sortedForChart.map((s, i) => {
      runningTotal += s.profit;
      return { name: `S${i + 1}`, profit: runningTotal };
    });
    return { totalProfit, totalHours, hourlyRate, winRate, chartData };
  }, [sessions]);

  const filteredSessions = useMemo(() => {
    return sessions
      .filter(s => 
        s.location.toLowerCase().includes(searchTerm.toLowerCase()) || 
        s.stakes.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.tags.some(t => t.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      .sort((a, b) => {
        let comparison = 0;
        if (sortField === 'date') comparison = a.date.localeCompare(b.date);
        else if (sortField === 'profit') comparison = a.profit - b.profit;
        else if (sortField === 'stakes') comparison = a.stakes.localeCompare(b.stakes);
        return sortOrder === 'asc' ? comparison : -comparison;
      });
  }, [sessions, searchTerm, sortField, sortOrder]);

  const sortedLabHistory = useMemo(() => {
    return [...labHistory].sort((a, b) => {
      let comparison = 0;
      if (labSortField === 'timestamp') {
        comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      } else if (labSortField === 'prompt') {
        comparison = a.prompt.localeCompare(b.prompt);
      }
      return labSortOrder === 'asc' ? comparison : -comparison;
    });
  }, [labHistory, labSortField, labSortOrder]);

  const insertFormatting = (prefix: string, suffix: string = '') => {
    if (!textareaRef.current) return;
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    const text = textareaRef.current.value;
    const before = text.substring(0, start);
    const selection = text.substring(start, end);
    const after = text.substring(end);
    const newText = before + prefix + selection + suffix + after;
    setLabPrompt(newText);
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        const newCursorPos = start + prefix.length + selection.length + suffix.length;
        textareaRef.current.setSelectionRange(newCursorPos, newCursorPos);
      }
    }, 0);
  };

  const startLiveSession = (stakes: string, location: string) => {
    setActiveSession({
      startTime: Date.now(),
      location,
      stakes,
      currentProfit: 0,
      isPaused: false,
      totalPausedTime: 0
    });
    setActiveTab('dashboard');
  };

  const pauseLiveSession = () => {
    if (!activeSession) return;
    const now = Date.now();
    setActiveSession({ ...activeSession, isPaused: true, pauseStart: now });
  };

  const resumeLiveSession = () => {
    if (!activeSession || !activeSession.pauseStart) return;
    const now = Date.now();
    const pausedFor = now - activeSession.pauseStart;
    setActiveSession({
      ...activeSession,
      isPaused: false,
      totalPausedTime: activeSession.totalPausedTime + pausedFor,
      pauseStart: undefined
    });
  };

  const stopLiveSession = () => {
    if (!activeSession) return;
    const finalDuration = (Date.now() - activeSession.startTime - activeSession.totalPausedTime) / (1000 * 60 * 60);
    const session: Session = {
      id: Date.now().toString(),
      date: new Date().toISOString().split('T')[0],
      location: activeSession.location,
      stakes: activeSession.stakes,
      duration: parseFloat(finalDuration.toFixed(2)),
      profit: activeSession.currentProfit,
      tags: ['Live Tracked'],
      mediaItems: []
    };
    setSessions(prev => [session, ...prev]);
    setActiveSession(null);
    setSessionTimer(0);
  };

  const sendToLab = (session: Session) => {
    const tagsContext = session.tags.length > 0 ? `[Tags: ${session.tags.join(', ')}]\n` : '';
    const prompt = `${tagsContext}**Session Analysis Request**
Date: ${session.date}
Location: ${session.location}
Stakes: ${session.stakes}
Profit/Loss: ${session.profit >= 0 ? '+' : ''}$${session.profit}
Duration: ${session.duration} hours

**Notes/History:**
${session.notes || 'No notes provided.'}

*Analyze my performance. Focus on GTO adherence.*`;
    setLabPrompt(prompt);
    if (session.mediaItems.length > 0) {
      setLabMedia({ data: session.mediaItems[0].data, type: session.mediaItems[0].type });
    } else {
      setLabMedia(null);
    }
    setActiveTab('lab');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const saveLabState = (promptVal: string, responseVal: string, tagsVal: string[], sizingVal: string | null, mediaVal: any) => {
    const item: LabHistoryItem = {
      id: `lab-${Date.now()}`,
      timestamp: new Date().toLocaleString(),
      prompt: promptVal,
      response: responseVal,
      strategicTags: tagsVal,
      sizingAdvice: sizingVal || undefined,
      media: mediaVal || undefined
    };
    setLabHistory(prev => [item, ...prev]);
  };

  const updateSessionNote = (id: string, notes: string) => {
    setSessions(prev => prev.map(s => s.id === id ? { ...s, notes } : s));
  };

  const handleDeepAnalysis = async (mode: 'thinking' | 'search' | 'maps' | 'sizing') => {
    setIsProcessing(true);
    setAiResponse(null);
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    try {
      const parts: any[] = [];
      if (labMedia) parts.push({ inlineData: { data: labMedia.data, mimeType: labMedia.type } });
      
      let finalPrompt = labPrompt;
      if (mode === 'sizing') {
        finalPrompt += `\n\n**ADDITIONAL REQUEST: SIZING OPTIMIZATION**\nCurrent Pot Size: ${potSize}. Please provide specific sizing suggestions for Continuation Bets, Value Bets, and Bluffs based on this pot. Suggest exact numbers for 1/3, 1/2, 2/3, Full Pot, and Overbets where theoretically appropriate.`;
      }
      
      parts.push({ text: finalPrompt || "Analyze this situation." });

      const responseSchema = {
        type: Type.OBJECT,
        properties: {
          analysis: { type: Type.STRING },
          strategicTags: { 
            type: Type.ARRAY, 
            items: { type: Type.STRING },
            description: "Detailed tags for strategy and table dynamics. Mandatory: Hero call, Value bet, Bluff, Semi-bluff, Hero position (e.g., BTN, CO), Table image."
          },
          sizingAdvice: { type: Type.STRING }
        },
        required: ["analysis", "strategicTags"]
      };

      const systemInstruction = `You are a world-class GTO poker coach and data scientist. 
      Examine the provided hand history or session notes.
      CRITICAL TASKS:
      1. Map all player actions to specific positions (BTN, SB, BB, UTG, HJ, CO).
      2. Identify high-level strategic markers: 'Bluff', 'Value Bet', 'Hero Call', 'Inductive Bet', 'Thin Value', 'Check-Raise'.
      3. Look for sizing tells or GTO deviations.
      4. If an image is provided, parse the board cards and stack sizes.
      
      Structure your response to be professional, theoretically grounded, and actionable.`;

      const config: any = {
        systemInstruction,
        responseMimeType: "application/json",
        responseSchema: responseSchema
      };

      if (mode === 'thinking') {
        config.thinkingConfig = { thinkingBudget: 32768 };
      }

      const response = await ai.models.generateContent({ 
        model: 'gemini-3-pro-preview', 
        contents: { parts }, 
        config 
      });

      const json = JSON.parse(response.text);
      setAiResponse(json.analysis);
      setLabStrategicTags(json.strategicTags || []);
      setLabSizingAdvice(json.sizingAdvice || null);
      
      saveLabState(labPrompt, json.analysis, json.strategicTags, json.sizingAdvice, labMedia);
    } catch (e: any) {
      setAiResponse(`Error: ${e.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTimer = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleLabSort = (field: LabSortField) => {
    if (labSortField === field) {
      setLabSortOrder(labSortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setLabSortField(field);
      setLabSortOrder('desc');
    }
  };

  const calculateSizing = (percentage: number) => {
    const numPot = parseFloat(potSize);
    if (isNaN(numPot)) return "0";
    return Math.floor(numPot * percentage).toString();
  };

  return (
    <div className="min-h-screen bg-[#0d0f12] text-gray-100 flex flex-col md:flex-row font-sans">
      <nav className="fixed bottom-0 left-0 right-0 bg-[#161b22] border-t border-gray-800 md:relative md:border-t-0 md:border-r md:w-20 lg:w-64 md:h-screen z-50 transition-all">
        <div className="p-6 hidden lg:block text-emerald-500 font-bold text-2xl tracking-tighter italic">ACE COACH</div>
        <div className="flex md:flex-col justify-around p-3 gap-2">
          <NavBtn icon={<BarChart3 />} label="Dashboard" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <NavBtn icon={<History />} label="Sessions" active={activeTab === 'sessions'} onClick={() => setActiveTab('sessions')} />
          <NavBtn icon={<BrainCircuit />} label="AI Lab" active={activeTab === 'lab'} onClick={() => setActiveTab('lab')} />
          <NavBtn icon={<Mic />} label="Live" active={activeTab === 'live'} onClick={() => setActiveTab('live')} />
          <NavBtn icon={<Sparkles />} label="Creative" active={activeTab === 'creative'} onClick={() => setActiveTab('creative')} />
        </div>
      </nav>

      <main className="flex-1 p-4 md:p-10 pb-24 md:pb-10 overflow-y-auto">
        
        {activeTab === 'dashboard' && (
          <section className="animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex justify-between items-center mb-8">
               <h1 className="text-4xl font-black bg-gradient-to-r from-emerald-400 to-emerald-600 bg-clip-text text-transparent uppercase italic">THE ARENA</h1>
               {activeSession ? (
                 <div className="flex items-center gap-4 bg-emerald-500/10 border border-emerald-500/30 px-6 py-3 rounded-2xl">
                    <div className="flex flex-col">
                      <span className="text-[10px] uppercase font-bold text-emerald-500 animate-pulse">Session Active: {activeSession.stakes}</span>
                      <span className="text-xl font-mono font-bold">{formatTimer(sessionTimer)}</span>
                    </div>
                    <div className="h-8 w-px bg-emerald-500/20" />
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] uppercase font-bold text-gray-500">Live P/L</span>
                      <span className={`text-xl font-bold ${activeSession.currentProfit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        ${activeSession.currentProfit}
                      </span>
                    </div>
                    <div className="flex gap-2 ml-4">
                      {activeSession.isPaused ? (
                        <button onClick={resumeLiveSession} className="p-2 bg-emerald-600 rounded-lg"><Play size={16}/></button>
                      ) : (
                        <button onClick={pauseLiveSession} className="p-2 bg-amber-600 rounded-lg"><Pause size={16}/></button>
                      )}
                      <button onClick={stopLiveSession} className="p-2 bg-red-600 rounded-lg"><Square size={16}/></button>
                    </div>
                 </div>
               ) : (
                 <button onClick={() => (document.getElementById('tracker-modal') as any).showModal()} className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-2xl font-bold uppercase tracking-widest text-xs transition-all shadow-lg shadow-emerald-500/20">
                   <Play size={16}/> Start Tracking
                 </button>
               )}
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <StatCard label="Bankroll" value={`$${stats.totalProfit}`} icon={<DollarSign className="text-emerald-400" />} />
              <StatCard label="Win Rate" value={`${stats.winRate.toFixed(1)}%`} icon={<Target className="text-emerald-400" />} />
              <StatCard label="Hourly" value={`$${stats.hourlyRate.toFixed(0)}/h`} icon={<Clock className="text-emerald-400" />} />
              <StatCard label="Volume" value={`${stats.totalHours}h`} icon={<TrendingUp className="text-emerald-400" />} />
            </div>
            
            <div className="bg-[#161b22] p-8 rounded-3xl border border-gray-800 shadow-2xl">
              <h3 className="text-xl font-bold mb-6 flex items-center gap-2 italic uppercase tracking-widest text-emerald-500/80"><BarChart3 size={20}/> Growth Trajectory</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stats.chartData}>
                    <defs>
                      <linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/><stop offset="95%" stopColor="#10b981" stopOpacity={0}/></linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" vertical={false} />
                    <XAxis dataKey="name" hide />
                    <YAxis stroke="#4a5568" fontSize={12} tickFormatter={(v) => `$${v}`} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{backgroundColor: '#1a202c', border: 'none', borderRadius: '12px'}} />
                    <Area type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={4} fill="url(#p)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'lab' && (
          <section className="max-w-4xl mx-auto space-y-6 pb-12">
            <div className="flex justify-between items-center">
              <h2 className="text-3xl font-bold italic tracking-tighter uppercase">RESEARCH LAB</h2>
              <div className="flex gap-2">
                <button onClick={() => setShowLabHistory(!showLabHistory)} className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-xl text-xs font-bold uppercase transition-all">
                  <FolderOpen size={16} /> History {labHistory.length > 0 && `(${labHistory.length})`}
                </button>
              </div>
            </div>

            {showLabHistory && (
              <div className="bg-[#161b22] border border-gray-800 rounded-3xl p-6 mb-6 space-y-4 animate-in slide-in-from-top-2">
                <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-800">
                  <h3 className="text-xs font-black uppercase tracking-widest text-emerald-500">Strategy Archives</h3>
                  <div className="flex items-center gap-4 text-[10px] font-bold text-gray-500 uppercase">
                    <button onClick={() => toggleLabSort('timestamp')} className={`flex items-center gap-1.5 ${labSortField === 'timestamp' ? 'text-emerald-400' : ''}`}>
                      <Clock size={12} /> Time {labSortField === 'timestamp' && (labSortOrder === 'asc' ? <SortAsc size={12}/> : <SortDesc size={12}/>)}
                    </button>
                    <button onClick={() => toggleLabSort('prompt')} className={`flex items-center gap-1.5 ${labSortField === 'prompt' ? 'text-emerald-400' : ''}`}>
                      <TypeIcon size={12} /> Content {labSortField === 'prompt' && (labSortOrder === 'asc' ? <SortAsc size={12}/> : <SortDesc size={12}/>)}
                    </button>
                  </div>
                </div>
                <div className="max-h-64 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                  {sortedLabHistory.map(item => (
                    <div key={item.id} className="p-4 bg-gray-900/50 rounded-2xl border border-gray-800 hover:border-emerald-500/30 cursor-pointer transition-all" 
                      onClick={() => { 
                        setLabPrompt(item.prompt); setAiResponse(item.response); 
                        setLabStrategicTags(item.strategicTags || []); setLabSizingAdvice(item.sizingAdvice || null);
                        setLabMedia(item.media || null); setShowLabHistory(false); 
                      }}>
                      <div className="flex justify-between text-[9px] text-gray-500 uppercase font-bold mb-2"><span>{item.timestamp}</span><ChevronRight size={10} /></div>
                      <p className="text-xs text-gray-300 line-clamp-2 italic">{item.prompt}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-[#161b22] rounded-3xl border border-gray-800 shadow-xl overflow-hidden">
              <div className="bg-gray-900/50 p-2 border-b border-gray-800 flex flex-wrap items-center gap-1">
                <button onClick={() => insertFormatting('**', '**')} title="Bold" className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white"><Bold size={16} /></button>
                <button onClick={() => insertFormatting('*', '*')} title="Italic" className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white"><Italic size={16} /></button>
                <div className="h-6 w-px bg-gray-800 mx-1" />
                <div className="flex gap-1 mr-1">
                  <button onClick={() => insertFormatting('### PRE-FLOP\n')} className="px-2 py-1 bg-gray-800 hover:bg-emerald-600/30 text-[10px] font-black uppercase rounded-md transition-all">Pre</button>
                  <button onClick={() => insertFormatting('### FLOP: [Ad 2h 7s]\n')} className="px-2 py-1 bg-gray-800 hover:bg-emerald-600/30 text-[10px] font-black uppercase rounded-md transition-all">Flop</button>
                  <button onClick={() => insertFormatting('### TURN: [Kh]\n')} className="px-2 py-1 bg-gray-800 hover:bg-emerald-600/30 text-[10px] font-black uppercase rounded-md transition-all">Turn</button>
                  <button onClick={() => insertFormatting('### RIVER: [Qs]\n')} className="px-2 py-1 bg-gray-800 hover:bg-emerald-600/30 text-[10px] font-black uppercase rounded-md transition-all">River</button>
                </div>
                <div className="h-6 w-px bg-gray-800 mx-1" />
                <div className="flex gap-1 mr-1">
                  <button onClick={() => insertFormatting('>>> HERO [CHECK]')} className="px-2 py-1 bg-blue-900/20 border border-blue-500/20 text-blue-400 text-[10px] font-black uppercase rounded-md transition-all">Check</button>
                  <button onClick={() => insertFormatting('>>> HERO [BET 50%]')} className="px-2 py-1 bg-emerald-900/20 border border-emerald-500/20 text-emerald-400 text-[10px] font-black uppercase rounded-md transition-all">Bet</button>
                  <button onClick={() => insertFormatting('>>> HERO [RAISE 3X]')} className="px-2 py-1 bg-purple-900/20 border border-purple-500/20 text-purple-400 text-[10px] font-black uppercase rounded-md transition-all">Raise</button>
                  <button onClick={() => insertFormatting('>>> HERO [FOLD]')} className="px-2 py-1 bg-red-900/20 border border-red-500/20 text-red-400 text-[10px] font-black uppercase rounded-md transition-all">Fold</button>
                </div>
                <div className="h-6 w-px bg-gray-800 mx-1" />
                <div className="flex items-center gap-1">
                  <UserCircle size={14} className="text-gray-500 ml-1" />
                  {['SB', 'BB', 'UTG', 'HJ', 'CO', 'BTN'].map(pos => (
                    <button key={pos} onClick={() => insertFormatting(`[${pos}] `)} className="px-1.5 py-0.5 bg-gray-800 hover:bg-gray-700 text-[9px] font-black text-gray-500 rounded transition-all">{pos}</button>
                  ))}
                </div>
              </div>

              <div className="relative p-1">
                <textarea 
                  ref={textareaRef} 
                  value={labPrompt} 
                  onChange={e => setLabPrompt(e.target.value)} 
                  placeholder="Record your hand history here. Strategic actions and positions are automatically identified..." 
                  className="w-full bg-[#0d0f12] border-none rounded-2xl p-6 h-72 focus:ring-0 outline-none resize-none font-mono text-sm leading-relaxed" 
                />
                {labMedia && (
                  <div className="absolute top-4 right-4 group">
                    <div className="relative w-20 h-20 rounded-xl overflow-hidden border-2 border-emerald-500 shadow-lg">
                      <img src={`data:${labMedia.type};base64,${labMedia.data}`} className="w-full h-full object-cover" />
                      <button onClick={() => setLabMedia(null)} className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity"><Trash2 size={16} className="text-red-400" /></button>
                    </div>
                  </div>
                )}
                <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between">
                  <label className="p-3 bg-gray-800/80 backdrop-blur rounded-xl cursor-pointer hover:bg-gray-700 transition-colors text-gray-400 flex items-center gap-2 border border-gray-700 shadow-lg">
                    <ImageIcon size={18} />
                    <span className="text-xs font-bold uppercase tracking-tighter">Attach Visual Context</span>
                    <input type="file" className="hidden" onChange={async e => {
                      const file = e.target.files?.[0];
                      if (file) setLabMedia({data: await blobToBase64(file), type: file.type});
                    }} />
                  </label>
                  <div className="flex items-center gap-2 text-gray-700 text-[10px] font-bold uppercase tracking-widest bg-black/20 px-3 py-1.5 rounded-full">
                    <Hash size={12}/> Analysis engine enabled
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-0 border-t border-gray-800">
                <button onClick={() => handleDeepAnalysis('thinking')} disabled={isProcessing} className="p-4 bg-emerald-600 hover:bg-emerald-500 font-bold flex flex-col items-center gap-2 transition-all"><BrainCircuit size={20} /><span className="text-[10px] uppercase tracking-widest">GTO Solve</span></button>
                <button onClick={() => handleDeepAnalysis('sizing')} disabled={isProcessing} className="p-4 bg-indigo-600 hover:bg-indigo-500 font-bold flex flex-col items-center gap-2 transition-all border-x border-gray-800/20"><Calculator size={20} /><span className="text-[10px] uppercase tracking-widest">Sizing</span></button>
                <button onClick={() => handleDeepAnalysis('search')} disabled={isProcessing} className="p-4 bg-blue-600 hover:bg-blue-500 font-bold flex flex-col items-center gap-2 transition-all"><Search size={20} /><span className="text-[10px] uppercase tracking-widest">Field Stats</span></button>
                <button onClick={() => handleDeepAnalysis('maps')} disabled={isProcessing} className="p-4 bg-gray-800 hover:bg-gray-700 font-bold flex flex-col items-center gap-2 transition-all border-l border-gray-800/20"><MapPin size={20} /><span className="text-[10px] uppercase tracking-widest">Venues</span></button>
              </div>
            </div>

            {isProcessing && <div className="flex flex-col items-center justify-center p-12 gap-4"><RefreshCw className="animate-spin text-emerald-500" size={40} /><p className="text-xs font-bold uppercase tracking-widest text-emerald-500/60 animate-pulse italic">Thinking...</p></div>}

            {aiResponse && (
              <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2 bg-[#161b22] p-6 rounded-3xl border border-gray-800">
                    <h3 className="text-xs font-black uppercase tracking-widest text-emerald-500 mb-4 flex items-center gap-2"><TagIcon size={14}/> Auto-Detected Strategy</h3>
                    <div className="flex flex-wrap gap-2">
                      {labStrategicTags.map((tag, idx) => (
                        <span key={idx} className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg text-[10px] font-bold uppercase transition-transform hover:scale-105">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="bg-[#161b22] p-6 rounded-3xl border border-gray-800 text-center flex flex-col justify-center">
                    <h3 className="text-xs font-black uppercase tracking-widest text-indigo-400 mb-2">Primary Recommendation</h3>
                    <div className="text-2xl font-black text-white italic">{labSizingAdvice || "N/A"}</div>
                  </div>
                </div>

                <div className="bg-[#161b22] p-8 rounded-3xl border border-gray-800 shadow-2xl">
                   <div className="flex items-center gap-2 text-emerald-500 mb-4">
                     <Sparkles size={18}/>
                     <span className="text-xs font-black uppercase tracking-[0.2em]">Coach Breakdown</span>
                   </div>
                  <div className="prose prose-invert max-w-none whitespace-pre-wrap text-gray-300 font-sans text-lg">{aiResponse}</div>
                </div>

                {/* New Sizing Calculator Section */}
                <div className="bg-[#161b22] rounded-3xl border border-gray-800 overflow-hidden shadow-2xl animate-in slide-in-from-bottom-4 delay-150">
                   <div className="bg-gray-900/50 p-6 border-b border-gray-800">
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-indigo-500/10 rounded-xl text-indigo-400">
                            <Coins size={20} />
                          </div>
                          <h3 className="text-sm font-black uppercase tracking-widest text-white">Sizing Laboratory</h3>
                        </div>
                        <div className="flex items-center bg-gray-950 border border-gray-800 rounded-2xl px-4 py-2">
                          <span className="text-[10px] font-black uppercase text-gray-500 mr-3">Pot</span>
                          <input 
                            type="number" 
                            value={potSize} 
                            onChange={(e) => setPotSize(e.target.value)}
                            className="bg-transparent text-sm font-bold text-emerald-400 outline-none w-20"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-5 gap-3">
                        {[
                          { label: '1/3', pct: 0.33, color: 'bg-emerald-500/10 text-emerald-400' },
                          { label: '1/2', pct: 0.50, color: 'bg-emerald-500/10 text-emerald-400' },
                          { label: '2/3', pct: 0.67, color: 'bg-emerald-500/10 text-emerald-400' },
                          { label: 'POT', pct: 1.00, color: 'bg-indigo-500/10 text-indigo-400' },
                          { label: '150%', pct: 1.50, color: 'bg-purple-500/10 text-purple-400' }
                        ].map((btn) => (
                          <button 
                            key={btn.label}
                            onClick={() => setCustomSizing(calculateSizing(btn.pct))}
                            className={`flex flex-col items-center justify-center p-3 rounded-2xl border border-gray-800 hover:border-emerald-500/50 transition-all ${btn.color}`}
                          >
                            <span className="text-[9px] font-black uppercase mb-1 opacity-60">{btn.label}</span>
                            <span className="text-sm font-black">${calculateSizing(btn.pct)}</span>
                          </button>
                        ))}
                      </div>
                   </div>

                   <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div>
                        <h4 className="text-[10px] font-black uppercase text-gray-500 mb-4 tracking-widest flex items-center gap-2">
                          <Dice5 size={12}/> Scenario Reference
                        </h4>
                        <div className="space-y-3">
                          {[
                            { title: 'Continuation Bet', desc: 'Usually 1/3 pot on dry boards, 2/3 on wet boards.', icon: <TrendingUp size={14} className="text-emerald-500"/> },
                            { title: 'Value Bet', desc: 'Sized to get called by the worst hands. Aim for 1/2 to 2/3 pot.', icon: <Coins size={14} className="text-indigo-500"/> },
                            { title: 'Bluff / Semi-Bluff', desc: 'Use polarized sizing. 3/4 pot or overbets to maximize fold equity.', icon: <Sparkles size={14} className="text-purple-500"/> }
                          ].map((item, idx) => (
                            <div key={idx} className="p-4 bg-gray-950/40 border border-gray-800 rounded-2xl hover:bg-gray-900/40 transition-colors">
                              <div className="flex items-center gap-2 mb-1">
                                {item.icon}
                                <span className="text-xs font-bold text-white">{item.title}</span>
                              </div>
                              <p className="text-[10px] text-gray-500 leading-relaxed">{item.desc}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="flex flex-col">
                        <h4 className="text-[10px] font-black uppercase text-gray-500 mb-4 tracking-widest flex items-center gap-2">
                          <Percent size={12}/> Exact Optimization
                        </h4>
                        <div className="flex-1 bg-gray-950/40 border border-gray-800 rounded-3xl p-6 flex flex-col justify-center items-center text-center">
                          {customSizing ? (
                            <div className="animate-in fade-in zoom-in-95">
                              <span className="text-[10px] font-black uppercase text-gray-500 mb-2 block">Target Bet Size</span>
                              <div className="text-4xl font-black text-emerald-400 mb-4">${customSizing}</div>
                              <button 
                                onClick={() => setCustomSizing(null)}
                                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-[10px] font-bold uppercase rounded-xl transition-all"
                              >
                                Reset
                              </button>
                            </div>
                          ) : (
                            <div className="text-gray-600">
                              <Calculator size={48} className="mx-auto mb-4 opacity-10" />
                              <p className="text-xs font-bold uppercase tracking-widest italic opacity-40">Select a pot % to optimize</p>
                            </div>
                          )}
                        </div>
                      </div>
                   </div>
                </div>
              </div>
            )}
          </section>
        )}

        {activeTab === 'sessions' && (
          <section className="max-w-5xl mx-auto space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <h2 className="text-2xl font-bold italic tracking-tighter uppercase">LOGBOOKS</h2>
              <div className="flex items-center gap-3">
                <div className="relative group flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
                  <input type="text" placeholder="Filter..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="bg-[#161b22] border border-gray-800 rounded-xl py-2 pl-10 pr-4 text-sm w-full md:w-64 outline-none focus:ring-1 focus:ring-emerald-500" />
                </div>
                <button onClick={() => (document.getElementById('add-modal') as any).showModal()} className="bg-emerald-600 p-2.5 rounded-xl hover:bg-emerald-500 transition-all"><PlusCircle size={20} /></button>
              </div>
            </div>

            <div className="space-y-4">
              {filteredSessions.map(s => (
                <div key={s.id} className="group">
                  <div onClick={() => setExpandedSessionId(expandedSessionId === s.id ? null : s.id)} className={`bg-[#161b22] border ${expandedSessionId === s.id ? 'border-emerald-500/50 rounded-t-2xl' : 'border-gray-800 rounded-2xl'} p-5 flex items-center justify-between cursor-pointer hover:bg-gray-800/40 transition-all`}>
                    <div className="flex items-center gap-4">
                      <div className={`p-4 rounded-2xl ${s.profit >= 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}><DollarSign size={20} /></div>
                      <div>
                        <div className="font-black text-xl flex items-baseline gap-2">
                          <span className={s.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}>${s.profit}</span>
                          <span className="text-xs font-normal text-gray-500 uppercase">{s.stakes}</span>
                        </div>
                        <div className="text-[10px] text-gray-500 uppercase font-bold mt-1">{s.date} • {s.location}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {s.mediaItems.length > 0 && <div className="flex -space-x-2">
                        {s.mediaItems.map(m => (
                          <div key={m.id} className="w-6 h-6 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-[8px] text-emerald-400" title={m.category}>{m.category[0]}</div>
                        ))}
                      </div>}
                      <button onClick={(e) => { e.stopPropagation(); setSessions(prev => prev.filter(x => x.id !== s.id)); }} className="text-gray-700 hover:text-red-500 p-2"><Trash2 size={18} /></button>
                      <ChevronDown size={20} className={`text-gray-600 transition-transform ${expandedSessionId === s.id ? 'rotate-180' : ''}`} />
                    </div>
                  </div>
                  {expandedSessionId === s.id && (
                    <div className="bg-[#1a202c] border-x border-b border-emerald-500/30 rounded-b-2xl p-6 animate-in slide-in-from-top-2">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="text-[10px] font-black uppercase text-gray-500 flex items-center gap-2 mb-2"><Notebook size={12}/> Notes</label>
                          <textarea value={s.notes || ''} onChange={(e) => updateSessionNote(s.id, e.target.value)} placeholder="Record reads..." className="w-full bg-[#0d0f12] border border-gray-800 rounded-xl p-4 h-40 focus:ring-1 focus:ring-emerald-500 outline-none font-mono text-sm" />
                        </div>
                        <div className="space-y-4">
                          <button onClick={() => sendToLab(s)} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-black uppercase tracking-widest py-3 rounded-xl flex items-center justify-center gap-2 transition-all"><ExternalLink size={16} /> Open in Lab</button>
                          
                          <div className="bg-[#0d0f12] p-4 rounded-xl border border-gray-800">
                             <div className="flex items-center justify-between mb-4">
                               <h4 className="text-[10px] font-black uppercase text-gray-500 flex items-center gap-2"><ImageIcon size={12}/> Media Gallery</h4>
                               <select 
                                 value={mediaFilter}
                                 onChange={(e) => setMediaFilter(e.target.value as MediaCategory)}
                                 className="bg-gray-800 border border-gray-700 rounded-lg text-[9px] uppercase font-bold text-gray-300 p-1 outline-none"
                               >
                                 <option value="All">All Categories</option>
                                 <option value="Hand Screenshot">Screenshots</option>
                                 <option value="Table View">Table View</option>
                                 <option value="Player Cam">Player Cam</option>
                                 <option value="Audio Note">Audio</option>
                               </select>
                             </div>
                             
                             <div className="grid grid-cols-3 gap-2">
                               {s.mediaItems
                                 .filter(m => mediaFilter === 'All' || m.category === mediaFilter)
                                 .map(m => (
                                   <div key={m.id} className="relative aspect-square rounded-lg overflow-hidden border border-gray-700 group cursor-pointer" onClick={() => {
                                      const win = window.open();
                                      win?.document.write(`<html><body style="margin:0;display:flex;align-items:center;justify-center;background:#000;"><img src="data:${m.type};base64,${m.data}" style="max-width:100%;max-height:100%;"></body></html>`);
                                   }}>
                                      <img src={`data:${m.type};base64,${m.data}`} className="w-full h-full object-cover" />
                                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-1 text-center">
                                        <Eye size={12} className="text-white mb-1" />
                                        <span className="text-[8px] font-bold uppercase text-white leading-tight">{m.category}</span>
                                      </div>
                                   </div>
                                 ))}
                               {s.mediaItems.length === 0 && <p className="col-span-3 text-center py-4 text-[9px] text-gray-600 uppercase italic">Empty vault.</p>}
                             </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      <dialog id="tracker-modal" className="modal bg-transparent p-0">
        <div className="bg-[#161b22] border border-gray-800 rounded-3xl p-8 max-sm w-full m-4 shadow-2xl backdrop-blur-xl">
          <h3 className="text-2xl font-bold mb-6 italic tracking-tighter uppercase">SIT DOWN</h3>
          <form className="space-y-4" onSubmit={e => {
            e.preventDefault();
            const stakes = (e.currentTarget.elements.namedItem('stakes') as HTMLInputElement).value;
            const loc = (e.currentTarget.elements.namedItem('loc') as HTMLInputElement).value;
            startLiveSession(stakes, loc);
            (document.getElementById('tracker-modal') as any).close();
          }}>
            <input name="stakes" placeholder="Stakes (e.g. 5/10 NL)" className="w-full bg-gray-900 border border-gray-800 p-4 rounded-xl outline-none focus:ring-1 focus:ring-emerald-500" required />
            <input name="loc" placeholder="Location" className="w-full bg-gray-900 border border-gray-800 p-4 rounded-xl outline-none focus:ring-1 focus:ring-emerald-500" required />
            <button type="submit" className="w-full bg-emerald-600 p-4 rounded-xl font-black uppercase tracking-widest shadow-lg shadow-emerald-500/20 active:scale-95 transition-all">Start Watch</button>
            <button type="button" onClick={() => (document.getElementById('tracker-modal') as any).close()} className="w-full bg-gray-800 p-4 rounded-xl">Cancel</button>
          </form>
        </div>
      </dialog>

      <dialog id="add-modal" className="modal bg-transparent p-0">
        <div className="bg-[#161b22] border border-gray-800 rounded-3xl p-8 max-w-md w-full m-4 shadow-2xl backdrop-blur-xl">
          <h3 className="text-2xl font-bold mb-6 italic tracking-tighter uppercase">LOG SESSION</h3>
          <form className="space-y-4" onSubmit={async (e) => {
            e.preventDefault();
            const newMedia: SessionMedia[] = [];
            const files = (document.getElementById('multi-files') as HTMLInputElement).files;
            const cat = (document.getElementById('media-cat') as HTMLSelectElement).value as any;
            if (files) {
              for (let i = 0; i < files.length; i++) {
                newMedia.push({ id: `m-${Date.now()}-${i}`, data: await blobToBase64(files[i]), type: files[i].type, category: cat });
              }
            }
            setSessions(p => [{ ...(newSession as Session), id: Date.now().toString(), mediaItems: newMedia }, ...p]);
            (document.getElementById('add-modal') as any).close();
          }}>
             <div className="grid grid-cols-2 gap-4">
               <input type="date" value={newSession.date} onChange={e => setNewSession({...newSession, date: e.target.value})} className="bg-gray-900 border border-gray-800 rounded-xl p-3 outline-none" />
               <input type="text" placeholder="Stakes" value={newSession.stakes} onChange={e => setNewSession({...newSession, stakes: e.target.value})} className="bg-gray-900 border border-gray-800 rounded-xl p-3 outline-none" />
             </div>
             <input type="text" placeholder="Location" value={newSession.location} onChange={e => setNewSession({...newSession, location: e.target.value})} className="w-full bg-gray-900 border border-gray-800 rounded-xl p-3 outline-none" />
             <div className="grid grid-cols-2 gap-4">
               <input type="number" placeholder="Hrs" value={newSession.duration} onChange={e => setNewSession({...newSession, duration: parseFloat(e.target.value)})} className="bg-gray-900 border border-gray-800 rounded-xl p-3 outline-none" />
               <input type="number" placeholder="Profit" value={newSession.profit} onChange={e => setNewSession({...newSession, profit: parseFloat(e.target.value)})} className="bg-gray-900 border border-gray-800 rounded-xl p-3 outline-none text-emerald-400 font-bold" />
             </div>
             <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase text-gray-500">Media Category</label>
                <select id="media-cat" className="w-full bg-gray-900 border border-gray-800 rounded-xl p-3 outline-none text-xs">
                  <option>Hand Screenshot</option>
                  <option>Table View</option>
                  <option>Player Cam</option>
                  <option>Audio Note</option>
                </select>
                <input id="multi-files" type="file" multiple className="w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-gray-800 file:text-emerald-400 cursor-pointer" />
             </div>
             <div className="flex gap-3 pt-4">
               <button type="button" onClick={() => (document.getElementById('add-modal') as any).close()} className="flex-1 p-3 bg-gray-800 rounded-xl">Discard</button>
               <button type="submit" className="flex-1 p-3 bg-emerald-600 rounded-xl font-bold uppercase tracking-widest shadow-lg shadow-emerald-500/20 active:scale-95 transition-all">Lock In</button>
             </div>
          </form>
        </div>
      </dialog>

      <style>{`
        .modal::backdrop { background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #3f444e; border-radius: 4px; }
        
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { 
          -webkit-appearance: none; 
          margin: 0; 
        }
      `}</style>
    </div>
  );
};

const NavBtn = ({ icon, label, active, onClick }: any) => (
  <button onClick={onClick} className={`flex flex-col lg:flex-row items-center gap-3 p-4 rounded-2xl transition-all duration-300 ${active ? 'bg-emerald-600/20 text-emerald-400' : 'text-gray-500 hover:bg-gray-800/50'}`}>
    {React.cloneElement(icon, { size: 24 })}
    <span className="text-[10px] lg:text-sm font-bold uppercase tracking-widest">{label}</span>
  </button>
);

const StatCard = ({ label, value, icon }: any) => (
  <div className="bg-[#161b22] border border-gray-800 p-6 rounded-3xl shadow-lg hover:border-emerald-500/30 transition-all group">
    <div className="flex items-center justify-between mb-4">
      <div className="p-3 bg-gray-900 rounded-2xl group-hover:bg-emerald-500/5 group-hover:text-emerald-400 transition-colors">{icon}</div>
    </div>
    <div className="text-gray-500 text-[10px] uppercase font-bold tracking-widest mb-1">{label}</div>
    <div className="text-2xl font-black">{value}</div>
  </div>
);

const container = document.getElementById('root');
if (container) createRoot(container).render(<PokerApp />);
