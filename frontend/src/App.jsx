import { useState, useEffect } from 'react';
import { Plus, Trash2, Clock, CheckCircle, XCircle, Play, Pause, Activity, TrendingUp, Zap, Calendar, Mail, FolderOpen, FileText, Search, AlertCircle } from 'lucide-react';
import AIAssistant from "./AIAssistant";
import HologramOrb from "./HologramOrb";

const API_URL = import.meta.env.VITE_API_URL || "https://uaos-backend.onrender.com/api";

function App() {
  const [tasks, setTasks] = useState([]);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [newTaskText, setNewTaskText] = useState('');
  const [newTaskSchedule, setNewTaskSchedule] = useState('manual');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('tasks');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [assistantOpen, setAssistantOpen] = useState(false);

  useEffect(() => {
    fetchTasks();
    fetchLogs();
    fetchStats();
    
    const interval = setInterval(() => {
      fetchTasks();
      fetchLogs();
      fetchStats();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {

  const refresh = () => {
    fetchTasks();
    fetchStats();
    fetchLogs();
  };

  window.addEventListener("refreshTasks", refresh);

  return () => window.removeEventListener("refreshTasks", refresh);

}, []);

  const fetchTasks = async () => {
  try {
    const res = await fetch(`${API_URL}/api/tasks`);

    if (!res.ok) {
      console.error("Tasks API failed:", res.status);
      setTasks([]);
      return;
    }

    const data = await res.json();
    setTasks(data.tasks || []);
  } catch (err) {
    console.error('Error:', err);
    setTasks([]);
  }
};
  const fetchLogs = async () => {
  try {
    const res = await fetch(`${API_URL}/api/logs`);

    if (!res.ok) {
      console.error("Logs API failed:", res.status);
      setLogs([]);
      return;
    }

    const data = await res.json();
    setLogs(data.logs || []);
  } catch (err) {
    console.error('Error:', err);
    setLogs([]);
  }
};

  const fetchStats = async () => {
  try {
    const res = await fetch(`${API_URL}/api/stats`);

    if (!res.ok) {
      console.error("Stats API failed:", res.status);
      setStats(null);
      return;
    }

    const data = await res.json();

    // SAFE STRUCTURE
    setStats({
      tasks: data.tasks || { total: 0, active: 0 },
      executions: data.executions || { total: 0, today: 0 }
    });

  } catch (err) {
    console.error('Error:', err);
    setStats(null);
  }
};

  const createTask = async () => {
    if (!newTaskText.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
        raw_text: newTaskText
        })
      });
      
      if (res.ok) {
        setNewTaskText('');
        setNewTaskSchedule('manual');
        fetchTasks();
        fetchStats();
      }
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await fetch(`${API_URL}/api/tasks/${taskId}`, { method: 'DELETE' });
      fetchTasks();
      fetchStats();
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const toggleTaskStatus = async (taskId, currentStatus) => {
    const newStatus = currentStatus === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
    try {
      await fetch(`${API_URL}/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchTasks();
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const executeTaskNow = async (taskId) => {
    try {
      await fetch(`${API_URL}/api/tasks/${taskId}/execute`, { method: 'POST' });
      setTimeout(() => {
        fetchTasks();
        fetchLogs();
        fetchStats();
      }, 1000);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const getWorkflowIcon = (type) => {
    switch (type) {
      case 'NEWS_DIGEST': return <Mail className="text-blue-400" size={20} />;
      case 'FILE_CLEANUP': return <FolderOpen className="text-purple-400" size={20} />;
      case 'INVOICE_SYNC': return <FileText className="text-green-400" size={20} />;
      default: return <Activity className="text-gray-400" size={20} />;
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      ACTIVE: 'bg-green-500/20 text-green-400 border-green-500/30',
      PAUSED: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      FAILED: 'bg-red-500/20 text-red-400 border-red-500/30'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[status] || styles.ACTIVE}`}>
        {status}
      </span>
    );
  };

  const formatDateTime = (dateStr) => {
  if (!dateStr) return 'Never';

  const date = new Date(dateStr);

  return date.toLocaleString('en-IN', { 
    timeZone: 'Asia/Kolkata',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  };

  const filteredTasks = (tasks || []).filter(task => {
    const matchesFilter = filterStatus === 'all' || task.status === filterStatus;
    const matchesSearch = task.raw_text.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const toggleAssistant = () => {
  setAssistantOpen(prev => !prev);
};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="flex w-screen h-screen overflow-hidden">
       <div className="flex-1 p-8 overflow-y-auto max-w-none">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg shadow-blue-500/25">
              <Zap size={32} />
            </div>
            <div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                UAOS Dashboard
              </h1>
              <p className="text-slate-400 text-lg mt-1">
                Unified AI Automation Operating System
              </p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && stats.tasks && stats.executions && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 backdrop-blur-sm border border-blue-500/20 rounded-2xl p-6 hover:border-blue-400/40 transition-all">
              <div className="flex items-center justify-between mb-3">
                <Activity className="text-blue-400" size={24} />
                <TrendingUp className="text-blue-400/40" size={20} />
              </div>
              <div className="text-3xl font-bold text-blue-400">{stats.tasks.total}</div>
              <div className="text-sm text-slate-400 mt-1">Total Tasks</div>
            </div>

            <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6 hover:border-green-400/40 transition-all">
              <div className="flex items-center justify-between mb-3">
                <CheckCircle className="text-green-400" size={24} />
                <Clock className="text-green-400/40" size={20} />
              </div>
              <div className="text-3xl font-bold text-green-400">{stats.tasks.active}</div>
              <div className="text-sm text-slate-400 mt-1">Active Tasks</div>
            </div>

            <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 backdrop-blur-sm border border-purple-500/20 rounded-2xl p-6 hover:border-purple-400/40 transition-all">
              <div className="flex items-center justify-between mb-3">
                <Zap className="text-purple-400" size={24} />
                <Calendar className="text-purple-400/40" size={20} />
              </div>
              <div className="text-3xl font-bold text-purple-400">{stats.executions.total}</div>
              <div className="text-sm text-slate-400 mt-1">Total Executions</div>
            </div>

            <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/5 backdrop-blur-sm border border-orange-500/20 rounded-2xl p-6 hover:border-orange-400/40 transition-all">
              <div className="flex items-center justify-between mb-3">
                <TrendingUp className="text-orange-400" size={24} />
                <Activity className="text-orange-400/40" size={20} />
              </div>
              <div className="text-3xl font-bold text-orange-400">{stats.executions.today}</div>
              <div className="text-sm text-slate-400 mt-1">Runs Today</div>
            </div>
          </div>
        )}

        {/* Create Task Card */}
        <div className="mb-8 bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-6">
            <Plus className="text-blue-400" size={24} />
            <h2 className="text-2xl font-bold">Create New Automation</h2>
          </div>
          <div>
            <textarea
              value={newTaskText}
              onChange={(e) => setNewTaskText(e.target.value)}
              placeholder="Type your automation in natural language...&#10;&#10;Examples:&#10;• Send me top 10 tech news every Friday at 6 PM to myemail@gmail.com&#10;• Clean my Downloads folder PDFs daily at 11 PM&#10;• Sync Gmail invoices to Drive every Monday"
              className="w-full bg-slate-800/50 border border-slate-600/50 rounded-xl p-4 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 mb-4 font-mono text-sm"
              rows="4"
            />
            
            <div className="flex gap-4 items-center">
              <select
                value={newTaskSchedule}
                onChange={(e) => setNewTaskSchedule(e.target.value)}
                className="bg-slate-800/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500"
              >
                <option value="manual">Manual</option>
                <option value="every minute">Every Minute (Testing)</option>
                <option value="hourly">Every Hour</option>
                <option value="daily">Daily (9 AM)</option>
                <option value="daily evening">Daily Evening (6 PM)</option>
                <option value="every monday">Every Monday</option>
                <option value="every friday">Every Friday</option>
              </select>
              
              <button
                onClick={createTask}
                disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-slate-600 disabled:to-slate-600 px-8 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all shadow-lg hover:shadow-blue-500/25"
              >
                <Plus size={20} />
                {loading ? 'Creating...' : 'Create Task'}
              </button>
            </div>
          </div>
        </div>

        {/* Tabs + Filters */}
        <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('tasks')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                activeTab === 'tasks' 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' 
                  : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
              }`}
            >
              Tasks ({(filteredTasks || []).length})
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                activeTab === 'logs' 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' 
                  : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
              }`}
            >
              Execution Logs ({(logs || []).length})
            </button>
          </div>

          {activeTab === 'tasks' && (
            <div className="flex gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search tasks..."
                  className="bg-slate-800/50 border border-slate-600/50 rounded-xl pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-slate-800/50 border border-slate-600/50 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Status</option>
                <option value="ACTIVE">Active</option>
                <option value="PAUSED">Paused</option>
                <option value="FAILED">Failed</option>
              </select>
            </div>
          )}
        </div>

        {/* Tasks Tab */}
        {activeTab === 'tasks' && (
          <div className="space-y-4">
            {(filteredTasks || []).length === 0 ? (
              <div className="text-center py-16 bg-slate-900/30 backdrop-blur-sm border border-slate-700/30 rounded-2xl">
                <AlertCircle size={48} className="mx-auto mb-4 text-slate-600" />
                <p className="text-slate-400 text-lg">No tasks found. Create your first automation above!</p>
              </div>
            ) : (
              (filteredTasks || []).map((task) => (
                <div
                  key={task.id}
                  className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 hover:border-slate-600/50 transition-all shadow-xl"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3 flex-wrap">
                        {getWorkflowIcon(task.parsed_type)}
                        {getStatusBadge(task.status)}
                        <span className="text-xs font-mono text-slate-500">#{task.id}</span>
                      </div>
                      
                      <p className="text-lg mb-4 text-slate-200">{task.raw_text}</p>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="text-slate-500 mb-1">Schedule</div>
                          <div className="text-slate-300 font-medium">{task.schedule}</div>
                        </div>
                        <div>
                          <div className="text-slate-500 mb-1">Next Run</div>
                          <div className="text-blue-400 font-medium">{formatDateTime(task.next_run)}</div>
                        </div>
                        <div>
                          <div className="text-slate-500 mb-1">Last Run</div>
                          <div className="text-slate-300 font-medium">{formatDateTime(task.last_run)}</div>
                        </div>
                        <div>
                          <div className="text-slate-500 mb-1">Total Runs</div>
                          <div className="text-purple-400 font-medium">{task.total_executions}</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 ml-6">
                      <button
                        onClick={() => executeTaskNow(task.id)}
                        className="p-3 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-xl transition-colors"
                        title="Execute Now"
                      >
                        <Play size={18} />
                      </button>
                      <button
                        onClick={() => toggleTaskStatus(task.id, task.status)}
                        className="p-3 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-xl transition-colors"
                        title={task.status === 'ACTIVE' ? 'Pause' : 'Resume'}
                      >
                        {task.status === 'ACTIVE' ? <Pause size={18} /> : <Play size={18} />}
                      </button>
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="p-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="space-y-3">
            {(logs || []).length === 0 ? (
              <div className="text-center py-16 bg-slate-900/30 backdrop-blur-sm border border-slate-700/30 rounded-2xl">
                <Activity size={48} className="mx-auto mb-4 text-slate-600" />
                <p className="text-slate-400 text-lg">No execution logs yet.</p>
              </div>
            ) : (
              (logs || []).map((log) => (
                <div
                  key={log.id}
                  className={`p-5 rounded-xl border-l-4 backdrop-blur-sm ${
                    log.status === 'SUCCESS' 
                      ? 'bg-green-500/5 border-green-500' 
                      : log.status === 'FAILED'
                      ? 'bg-red-500/5 border-red-500'
                      : 'bg-blue-500/5 border-blue-500'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <span className={`text-xs font-bold px-2 py-1 rounded ${
                          log.status === 'SUCCESS' ? 'bg-green-500/20 text-green-400' : 
                          log.status === 'FAILED' ? 'bg-red-500/20 text-red-400' : 
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {log.status}
                        </span>
                        <span className="text-xs text-slate-500">Task #{log.task_id}</span>
                        <span className="text-xs text-slate-600">{formatDateTime(log.start_time)}</span>
                      </div>
                      <p className="text-sm text-slate-300 mb-1">{log.task_text}</p>
                      <p className="text-xs text-slate-400">{log.message}</p>
                    </div>
                    {log.duration && (
                      <div className="text-xs text-slate-500 ml-4">
                        {log.duration.toFixed(1)}s
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
                </div>

      {/* AI Assistant Panel */}
      {assistantOpen && (
        <div className="w-[520px] min-w-[520px] border-l border-slate-800 bg-slate-950 h-full">
          <AIAssistant />
        </div>
      )}

      {/* AI Orb Button */}
      {!assistantOpen && <HologramOrb toggleAssistant={toggleAssistant} />}

    </div>
  </div>
);
}

export default App;