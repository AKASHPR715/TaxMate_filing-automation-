'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  X
} from 'lucide-react';

interface DocumentUpload {
  fileName: string | null;
  status: 'empty' | 'uploading' | 'completed' | 'error';
  progress: number;
}

export default function Dashboard() {
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

  const handleUpload = (
    event: React.ChangeEvent<HTMLInputElement>,
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>
  ) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      simulateUpload(files[0], setState);
    }
  };

  const handleDrop = (
    event: React.DragEvent,
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>,
    setIsDragging: (value: boolean) => void
  ) => {
    event.preventDefault();
    setIsDragging(false);
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      simulateUpload(files[0], setState);
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
  }: {
    title: string;
    description: string;
    state: DocumentUpload;
    setState: React.Dispatch<React.SetStateAction<DocumentUpload>>;
    isDragging: boolean;
    setIsDragging: (value: boolean) => void;
    inputId: string;
  }) => (
    <div
      onDragOver={handleDragOver}
      onDragEnter={() => setIsDragging(true)}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => handleDrop(e, setState, setIsDragging)}
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
        isDragging
          ? 'border-blue-900 bg-blue-50'
          : 'border-gray-300 hover:border-blue-900 hover:bg-gray-50'
      } ${state.status === 'completed' ? 'bg-green-50 border-green-300' : ''}`}
    >
      {state.status === 'empty' && (
        <>
          <Upload className={`h-12 w-12 mx-auto mb-3 ${
            isDragging ? 'text-blue-900' : 'text-gray-400'
          }`} />
          <p className="text-sm font-semibold text-gray-900 mb-1">{title}</p>
          <p className="text-xs text-gray-600 mb-3">{description}</p>
          <input
            type="file"
            onChange={(e) => handleUpload(e, setState)}
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Tax Filing Dashboard</h1>
          <p className="text-lg text-gray-600">
            Upload your documents and let our AI handle the rest
          </p>
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
              <p className="text-3xl font-bold text-gray-900">2024-25</p>
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
              <p className="text-3xl font-bold text-gray-900">₹45,000</p>
              <p className="text-sm text-green-600 mt-1 flex items-center">
                <TrendingUp className="h-4 w-4 mr-1" />
                ₹12,000 saved with deductions
              </p>
            </CardContent>
          </Card>

          <Card className="border-2">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Document Status</CardTitle>
                <AlertCircle className={`h-5 w-5 ${
                  allFilesUploaded ? 'text-green-600' : 'text-orange-600'
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
                <p className={`text-xs font-medium mt-3 ${
                  allFilesUploaded ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {allFilesUploaded ? '✓ All documents ready' : `${
                    [form16PartA, form16PartB, formAIS].filter(d => d.status === 'completed').length
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
                <CardTitle className="text-2xl">Upload Tax Documents</CardTitle>
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
                />

                <UploadZone
                  title="Form 16 - Part B"
                  description="Deductions and loss details"
                  state={form16PartB}
                  setState={setForm16PartB}
                  isDragging={isDraggingB}
                  setIsDragging={setIsDraggingB}
                  inputId="form16-b"
                />

                <UploadZone
                  title="Form AIS"
                  description="Interest income and other sources"
                  state={formAIS}
                  setState={setFormAIS}
                  isDragging={isDraggingAIS}
                  setIsDragging={setIsDraggingAIS}
                  inputId="form-ais"
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
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="income">Income</TabsTrigger>
                    <TabsTrigger value="deductions">Deductions</TabsTrigger>
                    <TabsTrigger value="summary">Summary</TabsTrigger>
                  </TabsList>

                  <TabsContent value="income" className="space-y-4 mt-4">
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">Salary Income</span>
                        <span className="text-lg font-bold text-blue-900">₹12,00,000</span>
                      </div>
                      <p className="text-sm text-gray-600">From Form 16</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">Other Income</span>
                        <span className="text-lg font-bold text-blue-900">₹50,000</span>
                      </div>
                      <p className="text-sm text-gray-600">Interest and dividends</p>
                    </div>
                  </TabsContent>

                  <TabsContent value="deductions" className="space-y-4 mt-4">
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">Section 80C</span>
                        <span className="text-lg font-bold text-green-600">₹1,50,000</span>
                      </div>
                      <p className="text-sm text-gray-600">PPF, ELSS, Life Insurance</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">HRA</span>
                        <span className="text-lg font-bold text-green-600">₹2,40,000</span>
                      </div>
                      <p className="text-sm text-gray-600">House Rent Allowance</p>
                    </div>
                  </TabsContent>

                  <TabsContent value="summary" className="mt-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center py-3 border-b">
                        <span className="text-gray-700">Total Income</span>
                        <span className="font-semibold text-gray-900">₹12,50,000</span>
                      </div>
                      <div className="flex justify-between items-center py-3 border-b">
                        <span className="text-gray-700">Total Deductions</span>
                        <span className="font-semibold text-green-600">-₹3,90,000</span>
                      </div>
                      <div className="flex justify-between items-center py-3 border-b">
                        <span className="text-gray-700">Taxable Income</span>
                        <span className="font-semibold text-gray-900">₹8,60,000</span>
                      </div>
                      <div className="flex justify-between items-center py-3 bg-blue-50 rounded-lg px-4">
                        <span className="font-semibold text-gray-900">Tax Liability</span>
                        <span className="text-xl font-bold text-blue-900">₹45,000</span>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>

                <div className="mt-6 flex gap-3">
                  <Button className="flex-1 bg-blue-900 hover:bg-blue-800">
                    <Download className="h-4 w-4 mr-2" />
                    Download Report
                  </Button>
                  <Button
                    disabled={!allFilesUploaded}
                    className={`flex-1 ${
                      allFilesUploaded
                        ? 'bg-green-600 hover:bg-green-700'
                        : 'bg-gray-300 cursor-not-allowed'
                    }`}
                  >
                    {allFilesUploaded ? 'Compute Tax' : 'Upload All Documents First'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="border-2 border-green-200 bg-green-50">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-6 w-6 text-green-600" />
                  <CardTitle className="text-xl">Chat with TaxMate</CardTitle>
                </div>
                <CardDescription>
                  Ask questions about your tax return
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-white rounded-lg p-4 mb-4 max-h-64 overflow-y-auto space-y-3">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <p className="text-sm text-gray-700">
                      Hello! I've analyzed your documents. How can I help you today?
                    </p>
                  </div>
                  <div className="bg-blue-900 text-white rounded-lg p-3 ml-8">
                    <p className="text-sm">
                      Can I claim more deductions?
                    </p>
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3">
                    <p className="text-sm text-gray-700">
                      Yes! I found you're eligible for Section 80D health insurance deductions. Have you paid any health insurance premiums this year?
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Type your question..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-900"
                  />
                  <Button className="bg-green-600 hover:bg-green-700">
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
      </div>
    </div>
  );
}
