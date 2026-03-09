'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { getUserId, getApiHeaders, isAuthenticated, logout } from '@/lib/user';
import { AuthModal } from '@/components/auth-modal';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  MessageSquare,
  Download,
  TrendingUp,
  IndianRupee,
  Calendar,
  X,
  Bot,
  Edit,
  Paperclip,
  Database
} from 'lucide-react';

import { useEffect, useRef } from 'react';
import { ReviewDataForm } from '@/components/review-data-form';
import { FilingViewer } from '@/components/filing-viewer';

interface DocumentUpload {
  fileName: string | null;
  status: 'empty' | 'uploading' | 'completed' | 'error';
  progress: number;
}

interface ChatMessage {
  type: 'message' | 'error' | 'status';
  content: string;
  sender: 'user' | 'bot';
}

export default function Dashboard() {
  // Analysis State
  const [analysis, setAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);

  // Review Modal State
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [extractedData, setExtractedData] = useState<Record<string, any>>({});
  const [editedDataJson, setEditedDataJson] = useState<string>("");

  // Step 3: View Filing Data
  const [showFilingViewer, setShowFilingViewer] = useState(false);

  // Authentication State
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);

  useEffect(() => {
    setIsUserLoggedIn(isAuthenticated());
  }, []);

  const requireAuth = () => {
    if (!isAuthenticated()) {
      setIsAuthModalOpen(true);
      return false;
    }
    return true;
  };

  const handleAuthSuccess = () => {
    setIsUserLoggedIn(true);
    // Optionally trigger a refresh or just close modal
  };

  const handleLogout = () => {
    logout();
    setIsUserLoggedIn(false);
  };

  // Step 1: Extract Data and Open Review Modal
  // Step 1: Extract Data and Open Review Modal (Now unified with View Saved Data)
  const fetchSavedData = async () => {
    if (!requireAuth()) return;
    setIsExtracting(true);
    try {
      const res = await fetch('http://localhost:8000/api/details/all', {
        headers: getApiHeaders()
      });
      if (!res.ok) throw new Error("Failed to fetch saved data");
      const allDocs = await res.json();

      const newExtractedData: Record<string, any> = {};

      if (allDocs.form16a && allDocs.form16a.length > 0) {
        const latest = allDocs.form16a[allDocs.form16a.length - 1];
        const id = latest.id || latest._id || 'saved';
        newExtractedData[`form16a_${id}`] = latest;
      }

      if (allDocs.form16b && allDocs.form16b.length > 0) {
        const latest = allDocs.form16b[allDocs.form16b.length - 1];
        const id = latest.id || latest._id || 'saved';
        newExtractedData[`form16b_${id}`] = latest;
      }

      if (allDocs.ais && allDocs.ais.length > 0) {
        const latest = allDocs.ais[allDocs.ais.length - 1];
        const id = latest.id || latest._id || 'saved';
        newExtractedData[`ais_${id}`] = latest;
      }

      setExtractedData(newExtractedData);
      setEditedDataJson(JSON.stringify(newExtractedData, null, 2));
      setShowReviewModal(true);
    } catch (e) {
      console.error("Error fetching/reviewing data", e);
    } finally {
      setIsExtracting(false);
    }
  };

  // Step 2: Submit Reviewed Data for Calculation
  const runCalculation = async () => {
    setIsAnalyzing(true);
    setShowReviewModal(false);
    try {
      // Note: The new /api/analyze endpoint fetches fresh data from DB using the orchestrator.
      // Current frontend edits are for client-side review only until persistence is updated.

      const res = await fetch('http://localhost:8000/api/analyze', {
        method: 'GET',
        headers: getApiHeaders()
      });

      if (!res.ok) throw new Error('Analysis failed');
      const data = await res.json();
      setAnalysis(data);
    } catch (e) {
      console.error("Analysis error:", e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Step 2b: Update DB and Calculate
  // Step 2b: Update DB and Calculate
  const handleUpdateAndCalculate = async () => {
    // 1. Prepare updates for the orchestrator
    const updatesList = Object.values(extractedData)
      .filter((doc: any) => doc && (doc._id || doc.id))
      .map((doc: any) => ({
        doc_id: doc.id || doc._id,
        updates: doc
      }));

    setIsAnalyzing(true);
    try {
      if (updatesList.length > 0) {
        // Call the review_and_calculate endpoint which handles updates + orchestration
        const res = await fetch('http://localhost:8000/api/orchestrator/review_and_calculate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...getApiHeaders()
          },
          body: JSON.stringify({
            updates: updatesList,
            force_restart: false
          })
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Review and calculate failed");
        }

        const data = await res.json();
        if (data.orchestrator_result) {
          setAnalysis(data.orchestrator_result);
        }

      } else {
        // No updates? just calculate
        await runCalculation();
      }

    } catch (e) {
      console.error("Failed to update and calculate", e);
      alert("An error occurred during calculation. Please try again.");
    } finally {
      setIsAnalyzing(false);
      setShowReviewModal(false); // Always close modal, even if there's an error
    }
  };

  // Step 2c: Update DB Only
  const handleUpdateOnly = async () => {
    setIsAnalyzing(true); // Reuse analyzing state for loading generic
    try {
      const updatesPromises = Object.values(extractedData).map(async (doc: any) => {
        const id = doc?.id || doc?._id;
        if (id) {
          try {
            await fetch(`http://localhost:8000/api/details/${id}`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                ...getApiHeaders()
              },
              body: JSON.stringify(doc)
            });
          } catch (e) {
            console.error(`Failed to update doc ${doc._id}`, e);
          }
        }
      });
      await Promise.all(updatesPromises);
      // Optional: Show a success toast or message?
    } catch (e) {
      console.error("Failed to save updates", e);
    } finally {
      setIsAnalyzing(false);
      setShowReviewModal(false);
    }
  };




  const [form16PartA, setForm16PartA] = useState<DocumentUpload>({

    fileName: null,
    status: 'empty',
    progress: 0,
  });

  const [form16PartB, setForm16PartB] = useState<DocumentUpload>({
    fileName: null,
    status: 'empty',
    progress: 0,
  });

  const [formAIS, setFormAIS] = useState<DocumentUpload>({
    fileName: null,
    status: 'empty',
    progress: 0,
  });

  const [isDraggingA, setIsDraggingA] = useState(false);
  const [isDraggingB, setIsDraggingB] = useState(false);
  const [isDraggingAIS, setIsDraggingAIS] = useState(false);

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatFileRef = useRef<HTMLInputElement>(null);
  const [isChatUploading, setIsChatUploading] = useState(false);

  // Scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket Connection
  useEffect(() => {
    const connectWebSocket = () => {
      const socket = new WebSocket('ws://localhost:8000/ws/chat');

      socket.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket Connected');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'message') {
            setMessages((prev) => [...prev, { type: 'message', content: data.content, sender: 'bot' }]);
          } else if (data.type === 'error') {
            setMessages((prev) => [...prev, { type: 'error', content: data.content, sender: 'bot' }]);
          }
        } catch (e) {
          console.error('Error parsing message:', e);
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket Disconnected. Reconnecting...');
        setTimeout(connectWebSocket, 3000);
      };

      socket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        socket.close();
      };

      ws.current = socket;
    };

    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const handleSendMessage = () => {
    if (!inputText.trim() || !ws.current || ws.current.readyState !== WebSocket.OPEN) return;

    const message = inputText.trim();

    // Add user message to UI immediately
    setMessages((prev) => [...prev, { type: 'message', content: message, sender: 'user' }]);

    // Send to backend as JSON
    ws.current.send(JSON.stringify({
      type: 'message',
      content: message
    }));

    // Clear input
    setInputText('');
  };

  const handleChatFileScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!requireAuth()) {
      // Clear file input so they can try again after login
      e.target.value = '';
      return;
    }

    const file = e.target.files?.[0];
    if (!file) return;

    // reset input
    e.target.value = '';

    setIsChatUploading(true);

    // 1. Determine doc_type
    const name = file.name.toLowerCase();
    let docType = 'form16a';
    if (name.includes('part_b') || name.includes('partb')) docType = 'form16b';
    else if (name.includes('ais')) docType = 'ais';
    else if (name.includes('26as')) docType = 'form26as';

    // 2. Upload and Extract
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    try {
      setMessages(prev => [...prev, { type: 'status', content: `Uploading and analyzing ${file.name}...`, sender: 'bot' }]);

      const res = await fetch(`http://localhost:8000/api/upload/${docType}`, {
        method: 'POST',
        headers: getApiHeaders(),
        body: formData
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      const extraction = data.data; // The actual JSON data

      // 3. Send Context to WebSocket
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({
          type: 'context_update',
          data: extraction
        }));

        // The backend will reply with a confirmation, but we can also handle UI here
      } else {
        setMessages(prev => [...prev, { type: 'error', content: "Chat disconnected. Please refresh.", sender: 'bot' }]);
      }

    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { type: 'error', content: "Failed to analyze document.", sender: 'bot' }]);
    } finally {
      setIsChatUploading(false);
    }
  };

  const allFilesUploaded =
    form16PartA.status === 'completed' &&
    form16PartB.status === 'completed' &&
    formAIS.status === 'completed';

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const simulateUpload = (
    file: File,
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>
  ) => {
    setState({
      fileName: file.name,
      status: 'uploading',
      progress: 0,
    });

    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 40;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setState({
          fileName: file.name,
          status: 'completed',
          progress: 100,
        });
      } else {
        setState((prev: DocumentUpload) => ({
          ...prev,
          progress,
        }));
      }
    }, 500);
  };

  const handleUpload = async (
    event: React.ChangeEvent<HTMLInputElement>,
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>,
    docType: string
  ) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      if (!requireAuth()) {
        // Clear file input
        event.target.value = '';
        return;
      }
      await uploadFile(files[0], setState, docType);
    }
  };

  const handleDrop = async (
    event: React.DragEvent,
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>,
    setIsDragging: (value: boolean) => void,
    docType: string
  ) => {
    event.preventDefault();
    setIsDragging(false);
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      if (!requireAuth()) return;
      await uploadFile(files[0], setState, docType);
    }
  };

  const uploadFile = async (
    file: File,
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>,
    docType: string
  ) => {
    setState({
      fileName: file.name,
      status: 'uploading',
      progress: 0,
    });

    const formData = new FormData();
    // Add prefix to filename based on docType
    const prefix = docType === 'form16a' ? 'form16a_' :
      docType === 'form16b' ? 'form16b_' :
        docType === 'ais' ? 'ais_' : '';

    // Create a new File object with the prefixed name
    const prefixedFile = new File([file], `${prefix}${file.name}`, { type: file.type });

    formData.append('file', prefixedFile);
    formData.append('doc_type', docType);

    try {
      // Pseudo-progress interval
      const interval = setInterval(() => {
        setState((prev) => {
          if (prev.progress >= 90) return prev;
          return { ...prev, progress: prev.progress + 10 };
        });
      }, 500);

      const response = await fetch(`http://localhost:8000/api/upload/${docType}`, {
        method: 'POST',
        headers: getApiHeaders(),
        body: formData,
      });

      clearInterval(interval);

      if (!response.ok) {
        if (response.status === 401) {
          setIsAuthModalOpen(true);
          throw new Error('Please login to continue');
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      console.log("Upload success:", data);

      setState({
        fileName: file.name,
        status: 'completed',
        progress: 100,
      });
    } catch (error) {
      console.error("Upload error:", error);
      setState({
        fileName: file.name,
        status: 'error',
        progress: 0,
      });
      // Optionally show toast or error message state here
    }
  };

  const clearUpload = (setState: React.Dispatch<React.SetStateAction<DocumentUpload>>) => {
    setState({
      fileName: null,
      status: 'empty',
      progress: 0,
    });
  };

  const UploadZone = ({
    title,
    description,
    state,
    setState,
    isDragging,
    setIsDragging,
    inputId,
    docType,
  }: {
    title: string;
    description: string;
    state: DocumentUpload;
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>;
    isDragging: boolean;
    setIsDragging: (value: boolean) => void;
    inputId: string;
    docType: string;
  }) => (
    <div
      onDragOver={handleDragOver}
      onDragEnter={() => setIsDragging(true)}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => handleDrop(e, setState, setIsDragging, docType)}
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${isDragging
        ? 'border-blue-900 bg-blue-50'
        : 'border-gray-300 hover:border-blue-900 hover:bg-gray-50'
        } ${state.status === 'completed' ? 'bg-green-50 border-green-300' : ''}`}
    >
      {state.status === 'empty' && (
        <>
          <Upload className={`h-12 w-12 mx-auto mb-3 ${isDragging ? 'text-blue-900' : 'text-gray-400'
            }`} />
          <p className="text-sm font-semibold text-gray-900 mb-1">{title}</p>
          <p className="text-xs text-gray-600 mb-3">{description}</p>
          <input
            type="file"
            onChange={(e) => handleUpload(e, setState, docType)}
            className="hidden"
            id={inputId}
            accept=".pdf,.json,.jpg,.jpeg,.png"
          />
          <label htmlFor={inputId}>
            <Button size="sm" className="bg-blue-900 hover:bg-blue-800" asChild>
              <span>Browse File</span>
            </Button>
          </label>
          <p className="text-xs text-gray-500 mt-3">PDF, JSON, JPG, PNG (Max 10MB)</p>
        </>
      )}

      {state.status === 'uploading' && (
        <div className="space-y-3">
          <div className="flex justify-center">
            <div className="animate-spin">
              <Upload className="h-8 w-8 text-blue-900" />
            </div>
          </div>
          <p className="text-sm font-medium text-gray-900">Uploading...</p>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-900 h-2 rounded-full transition-all duration-300"
              style={{ width: `${state.progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-600">{Math.round(state.progress)}%</p>
        </div>
      )}

      {state.status === 'completed' && (
        <div className="space-y-2">
          <div className="flex justify-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <p className="text-sm font-medium text-gray-900">Upload Complete</p>
          <div className="flex items-center justify-between bg-white rounded p-2 border border-green-200">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <FileText className="h-4 w-4 text-green-600 flex-shrink-0" />
              <p className="text-xs text-gray-700 truncate">{state.fileName}</p>
            </div>
            <button
              onClick={() => clearUpload(setState)}
              className="ml-2 flex-shrink-0 hover:text-red-600 transition-colors"
              aria-label="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="pt-16 bg-gray-50 min-h-screen">
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Tax Filing Dashboard</h1>
            <p className="text-lg text-gray-600">
              Upload your documents and let our AI handle the rest
            </p>
          </div>
          <div>
            {/* Login/Logout buttons removed - now in Navbar */}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <Card className="border-2">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Tax Year</CardTitle>
                <Calendar className="h-5 w-5 text-blue-900" />
              </div>
            </CardHeader>
            <CardContent>
              {analysis?.computation_result ? (
                <p className="text-3xl font-bold text-gray-900">2024-25</p>
              ) : (
                <p className="text-3xl font-bold text-gray-900">--</p>
              )}
              <p className="text-sm text-gray-600 mt-1">Assessment Year</p>
            </CardContent>
          </Card>

          <Card className="border-2">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Estimated Tax</CardTitle>
                <IndianRupee className="h-5 w-5 text-blue-900" />
              </div>
            </CardHeader>
            <CardContent>
              {analysis?.computation_result ? (
                <>
                  <p className="text-3xl font-bold text-gray-900">
                    ₹{analysis.computation_result.optimal_regime === 'NEW' ? analysis.computation_result.new_tax.toLocaleString() : analysis.computation_result.old_tax.toLocaleString()}
                  </p>
                  <p className="text-sm text-green-600 mt-1 flex items-center">
                    <TrendingUp className="h-4 w-4 mr-1" />
                    Regime: {analysis.computation_result.optimal_regime}
                  </p>
                </>
              ) : (
                <p className="text-xl text-gray-500">Pending...</p>
              )}
            </CardContent>
          </Card>

          <Card className="border-2">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Document Status</CardTitle>
                <AlertCircle className={`h-5 w-5 ${allFilesUploaded ? 'text-green-600' : 'text-orange-600'
                  }`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">Form 16-A</span>
                  {form16PartA.status === 'completed' ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">Form 16-B</span>
                  {form16PartB.status === 'completed' ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">Form AIS</span>
                  {formAIS.status === 'completed' ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                  )}
                </div>
                <p className={`text-xs font-medium mt-3 ${allFilesUploaded ? 'text-green-600' : 'text-orange-600'
                  }`}>
                  {allFilesUploaded ? '✓ All documents ready' : `${[form16PartA, form16PartB, formAIS].filter(d => d.status === 'completed').length
                    }/3 uploaded`}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-2xl flex justify-between items-center">
                  Upload Tax Documents
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-blue-900 border border-blue-200 hover:bg-blue-50"
                    onClick={fetchSavedData}
                    disabled={isExtracting}
                  >
                    <Database className="w-4 h-4 mr-2" />
                    View Saved Data
                  </Button>
                </CardTitle>
                <CardDescription>
                  Upload all three required documents to proceed. Each document is processed independently.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                <UploadZone
                  title="Form 16 - Part A"
                  description="Salary and TDS information"
                  state={form16PartA}
                  setState={setForm16PartA}
                  isDragging={isDraggingA}
                  setIsDragging={setIsDraggingA}
                  inputId="form16-a"
                  docType="form16a"
                />

                <UploadZone
                  title="Form 16 - Part B"
                  description="Deductions and loss details"
                  state={form16PartB}
                  setState={setForm16PartB}
                  isDragging={isDraggingB}
                  setIsDragging={setIsDraggingB}
                  inputId="form16-b"
                  docType="form16b"
                />

                <UploadZone
                  title="Form AIS"
                  description="Interest income and other sources"
                  state={formAIS}
                  setState={setFormAIS}
                  isDragging={isDraggingAIS}
                  setIsDragging={setIsDraggingAIS}
                  inputId="form-ais"
                  docType="ais"
                />
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-2xl">Analysis Preview</CardTitle>
                <CardDescription>
                  AI-extracted information from your documents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="income">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="income">Income</TabsTrigger>
                    <TabsTrigger value="summary">Summary</TabsTrigger>
                  </TabsList>

                  <TabsContent value="income" className="space-y-4 mt-4">
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">Salary Income</span>
                        <span className="text-lg font-bold text-blue-900">
                          ₹{analysis?.computation_result?.gross_salary ? analysis.computation_result.gross_salary.toLocaleString() : '0'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">From Form 16</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">Other Income</span>
                        <span className="text-lg font-bold text-blue-900">
                          ₹{analysis?.computation_result?.other_income ? analysis.computation_result.other_income.toLocaleString() : '0'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">Interest and dividends</p>
                    </div>
                  </TabsContent>


                  <TabsContent value="summary" className="mt-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center py-3 border-b">
                        <span className="text-gray-700">Gross Income</span>
                        <span className="font-semibold text-gray-900">
                          ₹{analysis?.computation_result ? (analysis.computation_result.gross_salary + analysis.computation_result.other_income).toLocaleString() : '0'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center py-3 border-b">
                        <span className="text-gray-700">Taxable Income</span>
                        <span className="font-semibold text-gray-900">
                          ₹{analysis?.computation_result ? (analysis.computation_result.optimal_regime === 'OLD' ? analysis.computation_result.old_taxable.toLocaleString() : analysis.computation_result.new_taxable.toLocaleString()) : '0'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center py-3 bg-blue-50 rounded-lg px-4">
                        <span className="font-semibold text-gray-900">Tax Liability ({analysis?.computation_result?.optimal_regime || 'EST'})</span>
                        <span className="text-xl font-bold text-blue-900">
                          ₹{analysis?.computation_result ? (analysis.computation_result.optimal_regime === 'NEW' ? analysis.computation_result.new_tax.toLocaleString() : analysis.computation_result.old_tax.toLocaleString()) : '0'}
                        </span>
                      </div>
                    </div>

                    {analysis?.advisory_result && (
                      <div className="mt-6 bg-green-50 p-4 rounded-lg border border-green-200">
                        <h3 className="font-bold text-green-900 mb-2 flex items-center">
                          <Bot className="h-5 w-5 mr-2" />
                          Advisor Recommendations
                        </h3>
                        <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                          {analysis.advisory_result}
                        </div>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>

                <div className="mt-6 flex gap-3">
                  <Button className="flex-1 bg-blue-900 hover:bg-blue-800">
                    <Download className="h-4 w-4 mr-2" />
                    Download Report
                  </Button>
                  <Button
                    disabled={!allFilesUploaded || isExtracting || isAnalyzing}
                    onClick={fetchSavedData}
                    className={`flex-1 ${allFilesUploaded
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-gray-300 cursor-not-allowed'
                      }`}
                  >
                    {isExtracting
                      ? 'Extracting Data...'
                      : (isAnalyzing
                        ? 'Analyzing...'
                        : (allFilesUploaded ? 'Review & Calculate' : 'Upload All Documents First')
                      )
                    }
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowFilingViewer(true)}
                    className="flex-1 border-blue-900 text-blue-900 hover:bg-blue-50"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    View ITR Data
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="border-2 border-green-200 bg-green-50 flex flex-col h-[600px]">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-6 w-6 text-green-600" />
                  <CardTitle className="text-xl">Chat with TaxMate</CardTitle>
                </div>
                <CardDescription>
                  Ask questions about your tax return
                  <span className={`ml-2 inline-block w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} title={isConnected ? "Connected" : "Disconnected"} />
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col min-h-0">
                <div className="bg-white rounded-lg p-4 mb-4 flex-1 overflow-y-auto space-y-3">
                  {messages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-10">
                      <p>Start a conversation to get tax advice!</p>
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`rounded-lg p-3 max-w-[80%] ${msg.sender === 'user'
                          ? 'bg-blue-900 text-white ml-auto'
                          : 'bg-gray-100 text-gray-800'
                          }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>
                <div className="flex gap-2">
                  <input
                    type="file"
                    ref={chatFileRef}
                    className="hidden"
                    onChange={handleChatFileScan}
                    accept=".pdf,.json,.jpg,.png"
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    disabled={!isConnected || isChatUploading}
                    onClick={() => chatFileRef.current?.click()}
                    title="Upload document for context"
                  >
                    <Paperclip className="h-4 w-4 text-gray-600" />
                  </Button>
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your question..."
                    disabled={!isConnected}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-900 disabled:bg-gray-100"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!isConnected || !inputText.trim()}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Send
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-xl">Quick Tips</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-900 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-gray-700">
                    Upload Form 16-A first for salary details
                  </p>
                </div>
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-900 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-gray-700">
                    All three documents must be uploaded to compute tax
                  </p>
                </div>
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-900 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-gray-700">
                    Review AI suggestions before final filing
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Review Modal */}
        <Dialog open={showReviewModal} onOpenChange={setShowReviewModal}>
          <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
            <DialogHeader>
              <DialogTitle className="flex items-center">
                <Edit className="h-5 w-5 mr-2 text-blue-900" />
                Review Extracted Data
              </DialogTitle>
              <DialogDescription>
                We extracted the following data from your documents. Please review and modify if necessary before we calculate your taxes.
              </DialogDescription>
            </DialogHeader>

            <Tabs defaultValue="form" className="flex-1 flex flex-col min-h-0 mt-4">
              <TabsList className="grid w-[200px] grid-cols-2">
                <TabsTrigger value="form">Form</TabsTrigger>
                <TabsTrigger value="json">JSON</TabsTrigger>
              </TabsList>

              {/* Fixed Form Tab - Now Scrollable */}
              <TabsContent value="form" className="flex-1 overflow-y-auto mt-4 border rounded-md">
                <div className="p-4">
                  <ReviewDataForm
                    data={extractedData}
                    onUpdate={(newData: Record<string, any>) => {
                      setExtractedData(newData);
                      setEditedDataJson(JSON.stringify(newData, null, 2));
                    }}
                  />
                </div>
              </TabsContent>

              {/* Fixed JSON Tab - Now Scrollable */}
              <TabsContent value="json" className="flex-1 overflow-hidden mt-4">
                <div className="h-full overflow-y-auto border rounded-md">
                  <Textarea
                    className="font-mono text-sm w-full min-h-[400px] resize-none border-0 focus-visible:ring-0"
                    value={editedDataJson}
                    onChange={(e) => {
                      setEditedDataJson(e.target.value);
                      try {
                        setExtractedData(JSON.parse(e.target.value));
                      } catch (err) {
                        // invalid json, don't update object state yet
                      }
                    }}
                  />
                </div>
              </TabsContent>
            </Tabs>

            <DialogFooter className="mt-4">
              <Button variant="outline" onClick={() => setShowReviewModal(false)}>Cancel</Button>
              <Button variant="outline" onClick={handleUpdateOnly} className="border-blue-200 text-blue-900 hover:bg-blue-50">
                Update Data
              </Button>
              <Button
                onClick={handleUpdateAndCalculate}
                className="bg-green-600 hover:bg-green-700"
                disabled={isAnalyzing}
              >
                {isAnalyzing ? 'Processing...' : 'Confirm & Calculate'}
              </Button>

            </DialogFooter>
          </DialogContent>
        </Dialog>

        <FilingViewer
          open={showFilingViewer}
          onOpenChange={setShowFilingViewer}
          itrType="ITR1"
        />
      </div>
    </div>
  );
}
