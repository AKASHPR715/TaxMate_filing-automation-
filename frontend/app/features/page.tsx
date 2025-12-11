'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Bot,
  Shield,
  Zap,
  BarChart3,
  MessageSquare,
  FileCheck,
  Clock,
  Lock,
  Brain,
  Database,
  RefreshCw,
  CheckCircle
} from 'lucide-react';

export default function Features() {
  const [activeTab, setActiveTab] = useState('automation');

  const features = [
    {
      icon: Bot,
      title: 'AI Multi-Agent System',
      description: 'Multiple specialized AI agents work together to handle different aspects of your tax filing, from document processing to deduction optimization.',
      benefits: [
        'Coordinated agent workflows',
        'Specialized processing for each document type',
        'Intelligent decision-making system',
        'Continuous learning and improvement'
      ]
    },
    {
      icon: Shield,
      title: 'Secure Document Processing',
      description: 'Bank-level encryption and security protocols ensure your sensitive financial information remains completely protected throughout the process.',
      benefits: [
        'End-to-end encryption',
        'Secure cloud storage',
        'Privacy-first architecture',
        'Compliance with data protection laws'
      ]
    },
    {
      icon: Zap,
      title: 'Real-Time Computation',
      description: 'Instant tax calculations as you upload documents. See your tax liability, refund amount, and deductions update in real-time.',
      benefits: [
        'Instant results',
        'Dynamic tax calculations',
        'Live deduction tracking',
        'Scenario planning tools'
      ]
    },
    {
      icon: BarChart3,
      title: 'Personalized Dashboards',
      description: 'Beautiful, intuitive dashboards show your complete tax picture with charts, insights, and actionable recommendations.',
      benefits: [
        'Visual tax breakdown',
        'Historical comparison',
        'Savings opportunities',
        'Custom reports generation'
      ]
    },
    {
      icon: Brain,
      title: 'Intelligent OCR',
      description: 'Advanced optical character recognition powered by deep learning extracts data from any document format with exceptional accuracy.',
      benefits: [
        'Supports multiple file formats',
        'Handles poor quality scans',
        'Multi-language support',
        '99%+ accuracy rate'
      ]
    },
    {
      icon: Database,
      title: 'Smart Data Validation',
      description: 'Automated cross-verification of information across multiple documents ensures accuracy and catches potential errors before filing.',
      benefits: [
        'Automatic error detection',
        'Consistency checking',
        'Missing information alerts',
        'Duplicate detection'
      ]
    },
    {
      icon: RefreshCw,
      title: 'Auto-Update Tax Rules',
      description: 'System automatically updates with latest tax laws, deductions, and regulations. Always compliant with current Indian tax code.',
      benefits: [
        'Real-time rule updates',
        'Compliance guarantee',
        'New deduction alerts',
        'Tax law notifications'
      ]
    },
    {
      icon: Clock,
      title: 'Save Time',
      description: 'What used to take hours or days now takes minutes. Our AI handles the complexity while you focus on reviewing the results.',
      benefits: [
        'Average filing time: 15 minutes',
        'Bulk document processing',
        'Auto-fill from previous years',
        'One-click amendments'
      ]
    },
  ];

  return (
    <div className="pt-16">
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Powerful Features
          </h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            TaxMate combines cutting-edge AI technology with user-friendly design
            to deliver the most advanced tax filing experience available.
          </p>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="border-2 hover:border-blue-900 transition-all duration-300 hover:shadow-lg group">
                <CardHeader>
                  <div className="w-14 h-14 bg-blue-100 group-hover:bg-blue-900 rounded-lg flex items-center justify-center mb-4 transition-colors">
                    <feature.icon className="h-8 w-8 text-blue-900 group-hover:text-white transition-colors" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {feature.benefits.map((benefit, idx) => (
                      <li key={idx} className="flex items-start text-sm text-gray-600">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                        <span>{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Interactive Features
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience our intelligent tools designed to make tax filing intuitive
            </p>
          </div>

          <Tabs defaultValue="explain" className="max-w-4xl mx-auto">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="explain">Explain My Tax</TabsTrigger>
              <TabsTrigger value="chat">AI Chat Assistant</TabsTrigger>
            </TabsList>

            <TabsContent value="explain" className="mt-8">
              <Card className="border-2">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FileCheck className="h-6 w-6 text-blue-900" />
                    </div>
                    <div>
                      <CardTitle className="text-2xl">Explain My Tax</CardTitle>
                      <CardDescription>
                        Get plain-English explanations of complex tax concepts
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                    <p className="text-gray-700 mb-4">
                      <strong>Example Query:</strong> "Why is my tax liability higher this year?"
                    </p>
                    <div className="bg-white rounded p-4 border border-blue-300">
                      <p className="text-gray-600 text-sm leading-relaxed">
                        Your tax liability increased by ₹15,000 this year primarily due to two factors:
                        <br /><br />
                        1. Your income increased from ₹8,00,000 to ₹9,50,000, moving you into a higher tax bracket.
                        <br />
                        2. You claimed ₹30,000 less in 80C deductions compared to last year.
                        <br /><br />
                        However, I've identified ₹25,000 in additional HRA deductions you're eligible for that could reduce your liability.
                      </p>
                    </div>
                  </div>
                  <p className="text-gray-600">
                    Our AI breaks down your tax situation into simple terms, helping you understand
                    exactly where your money goes and how to optimize your return.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="chat" className="mt-8">
              <Card className="border-2">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <MessageSquare className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <CardTitle className="text-2xl">AI Chat Assistant</CardTitle>
                      <CardDescription>
                        24/7 intelligent support for all your tax questions
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-green-50 rounded-lg p-6 border border-green-200 space-y-3">
                    <div className="flex gap-3">
                      <div className="bg-white rounded-lg p-3 border border-green-300 flex-1">
                        <p className="text-sm text-gray-700">Can I claim home loan interest as a deduction?</p>
                      </div>
                    </div>
                    <div className="flex gap-3 justify-end">
                      <div className="bg-green-600 text-white rounded-lg p-3 flex-1">
                        <p className="text-sm">
                          Yes! You can claim home loan interest up to ₹2,00,000 under Section 24(b).
                          I see you have a home loan in your documents. Would you like me to calculate
                          your eligible deduction?
                        </p>
                      </div>
                    </div>
                  </div>
                  <p className="text-gray-600">
                    Ask anything about tax laws, deductions, filing status, or your specific tax situation.
                    Our AI provides accurate, contextual answers based on your documents.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      <section className="py-20 bg-gradient-to-br from-blue-50 to-green-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-3xl mx-auto">
            <Lock className="h-16 w-16 text-blue-900 mx-auto mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Security You Can Trust
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Your financial data is protected with military-grade encryption. We never share
              your information with third parties and comply with all Indian data protection regulations.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
              <div className="bg-white rounded-lg p-6 border-2 border-blue-900">
                <Shield className="h-8 w-8 text-blue-900 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">256-bit Encryption</h3>
                <p className="text-sm text-gray-600">Same security used by major banks</p>
              </div>
              <div className="bg-white rounded-lg p-6 border-2 border-blue-900">
                <Lock className="h-8 w-8 text-green-600 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Zero Data Sharing</h3>
                <p className="text-sm text-gray-600">Your data stays completely private</p>
              </div>
              <div className="bg-white rounded-lg p-6 border-2 border-blue-900">
                <CheckCircle className="h-8 w-8 text-blue-900 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Fully Compliant</h3>
                <p className="text-sm text-gray-600">Meets all regulatory requirements</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
