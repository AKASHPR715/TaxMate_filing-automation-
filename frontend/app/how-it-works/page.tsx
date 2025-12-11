'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Upload, ScanSearch, Calculator, TrendingDown, CheckCircle2 } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      number: '01',
      title: 'Upload Tax Documents',
      description: 'Simply drag and drop your Form 16, salary slips, investment proofs, and other tax documents. Our system supports PDF, JSON, and image formats for maximum convenience.',
      icon: Upload,
      color: 'blue',
    },
    {
      number: '02',
      title: 'AI Information Extraction',
      description: 'Advanced AI agents automatically scan and extract relevant information from your documents. Smart OCR technology ensures accurate data capture from any document type.',
      icon: ScanSearch,
      color: 'green',
    },
    {
      number: '03',
      title: 'Tax Computation',
      description: 'Our intelligent system calculates your tax liability based on current Indian tax laws. It considers your income, deductions, and exemptions to provide accurate results.',
      icon: Calculator,
      color: 'blue',
    },
    {
      number: '04',
      title: 'Deduction & Exemption Finder',
      description: 'AI-powered analysis identifies all eligible deductions under Section 80C, 80D, HRA, and more. Maximize your savings with personalized recommendations.',
      icon: TrendingDown,
      color: 'green',
    },
    {
      number: '05',
      title: 'Filing & Validation',
      description: 'Review your complete tax return, validate all entries, and file directly through our secure platform. Get real-time status updates and acknowledgment receipts.',
      icon: CheckCircle2,
      color: 'blue',
    },
  ];

  return (
    <div className="pt-16">
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            How TaxMate Works
          </h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Filing your taxes has never been easier. Follow our simple 5-step process
            powered by artificial intelligence to complete your tax return in minutes.
          </p>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-16">
            {steps.map((step, index) => (
              <div
                key={step.number}
                className="relative"
              >
                <Card className="overflow-hidden border-2 hover:border-blue-900 transition-all duration-300 hover:shadow-xl">
                  <CardContent className="p-0">
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-0">
                      <div className={`md:col-span-5 ${
                        step.color === 'blue' ? 'bg-gradient-to-br from-blue-50 to-blue-100' : 'bg-gradient-to-br from-green-50 to-green-100'
                      } p-8 flex items-center justify-center`}>
                        <div className="text-center">
                          <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${
                            step.color === 'blue' ? 'bg-blue-900' : 'bg-green-600'
                          } mb-6`}>
                            <step.icon className="h-12 w-12 text-white" />
                          </div>
                          <div className={`text-6xl font-bold ${
                            step.color === 'blue' ? 'text-blue-900' : 'text-green-600'
                          } opacity-20`}>
                            {step.number}
                          </div>
                        </div>
                      </div>

                      <div className="md:col-span-7 p-8 bg-white flex items-center">
                        <div>
                          <h3 className="text-3xl font-bold text-gray-900 mb-4">
                            {step.title}
                          </h3>
                          <p className="text-lg text-gray-600 leading-relaxed">
                            {step.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {index < steps.length - 1 && (
                  <div className="flex justify-center my-8">
                    <div className="w-1 h-12 bg-gradient-to-b from-blue-900 to-green-600 rounded-full"></div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-br from-blue-50 to-green-50 rounded-3xl p-12 text-center border-2 border-blue-900">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Ready to Experience Effortless Tax Filing?
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Join thousands of users who have simplified their tax returns with TaxMate's
              intelligent automation system.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/dashboard"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white bg-blue-900 rounded-lg hover:bg-blue-800 transition-colors"
              >
                Start Your Tax Filing
              </a>
              <a
                href="/features"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-blue-900 bg-white border-2 border-blue-900 rounded-lg hover:bg-blue-50 transition-colors"
              >
                Explore Features
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
