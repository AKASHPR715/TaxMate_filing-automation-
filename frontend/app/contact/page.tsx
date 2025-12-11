'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Mail, MessageSquare, Send, CheckCircle } from 'lucide-react';

export default function Contact() {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 5000);
  };

  const faqs = [
    {
      question: 'How secure is my data on TaxMate?',
      answer: 'Your data is protected with bank-level 256-bit encryption. We never share your information with third parties and comply with all Indian data protection regulations. All documents are stored securely and deleted after your filing is complete unless you choose to keep them for future reference.',
    },
    {
      question: 'What documents do I need to upload?',
      answer: 'Typically, you\'ll need Form 16 (from your employer), bank statements, investment proofs (PPF, ELSS, insurance), home loan certificates, rent receipts, and any other income documents. TaxMate will guide you through the process and tell you if any documents are missing.',
    },
    {
      question: 'How accurate are the tax calculations?',
      answer: 'Our AI system is trained on current Indian tax laws and regulations. The calculations are cross-verified by multiple AI agents to ensure accuracy. However, we always recommend reviewing the final return before filing. For complex tax situations, we suggest consulting with a tax professional.',
    },
    {
      question: 'Can I file for previous years?',
      answer: 'Yes, TaxMate supports filing for previous assessment years. The system automatically adjusts tax rules and calculations based on the selected year. You can also file revised returns if you need to correct a previously filed return.',
    },
    {
      question: 'Is TaxMate suitable for business income?',
      answer: 'Currently, TaxMate is optimized for salaried individuals with investment income. We\'re working on expanding support for business income, freelancers, and more complex tax scenarios in future updates.',
    },
    {
      question: 'What if the AI makes a mistake?',
      answer: 'While our AI is highly accurate, you have full control to review and modify all calculations before filing. The system shows all extracted data and calculations transparently. You can also use our AI chat assistant to understand any part of your tax return.',
    },
    {
      question: 'How long does the filing process take?',
      answer: 'Most users complete their tax filing in 15-20 minutes. The AI processes documents instantly, and you just need to review the results. Complex returns with multiple income sources may take a bit longer.',
    },
    {
      question: 'Do I need to create an account?',
      answer: 'Currently, TaxMate is in demo mode as a research project. For the full production version, users will need to create an account to securely save their tax information and track their filing history.',
    },
  ];

  return (
    <div className="pt-16">
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Contact Us
          </h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Have questions? We're here to help. Send us a message or check out our FAQ.
          </p>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <Card className="border-2">
                <CardHeader>
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <MessageSquare className="h-6 w-6 text-blue-900" />
                    </div>
                    <CardTitle className="text-3xl">Send us a Message</CardTitle>
                  </div>
                  <CardDescription className="text-base">
                    Fill out the form below and we'll get back to you as soon as possible
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {submitted ? (
                    <div className="bg-green-50 border-2 border-green-600 rounded-lg p-8 text-center">
                      <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        Message Sent!
                      </h3>
                      <p className="text-gray-600">
                        Thank you for contacting us. We'll respond within 24 hours.
                      </p>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmit} className="space-y-6">
                      <div>
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                          Your Name
                        </label>
                        <Input
                          id="name"
                          type="text"
                          required
                          placeholder="John Doe"
                          className="w-full"
                        />
                      </div>

                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                          Email Address
                        </label>
                        <Input
                          id="email"
                          type="email"
                          required
                          placeholder="john@example.com"
                          className="w-full"
                        />
                      </div>

                      <div>
                        <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                          Subject
                        </label>
                        <Input
                          id="subject"
                          type="text"
                          required
                          placeholder="How can we help you?"
                          className="w-full"
                        />
                      </div>

                      <div>
                        <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                          Message
                        </label>
                        <Textarea
                          id="message"
                          required
                          placeholder="Tell us more about your question or feedback..."
                          className="w-full min-h-32"
                        />
                      </div>

                      <Button type="submit" className="w-full bg-blue-900 hover:bg-blue-800 text-lg py-6">
                        <Send className="mr-2 h-5 w-5" />
                        Send Message
                      </Button>
                    </form>
                  )}
                </CardContent>
              </Card>

              <Card className="border-2 mt-6">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <Mail className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">Email Us Directly</CardTitle>
                      <CardDescription>For immediate assistance</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium text-gray-700">General Inquiries</p>
                      <a href="mailto:support@taxmate.ai" className="text-blue-900 hover:underline">
                        support@taxmate.ai
                      </a>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Technical Support</p>
                      <a href="mailto:tech@taxmate.ai" className="text-blue-900 hover:underline">
                        tech@taxmate.ai
                      </a>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Partnership Inquiries</p>
                      <a href="mailto:partners@taxmate.ai" className="text-blue-900 hover:underline">
                        partners@taxmate.ai
                      </a>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div>
              <Card className="border-2">
                <CardHeader>
                  <CardTitle className="text-3xl">Frequently Asked Questions</CardTitle>
                  <CardDescription className="text-base">
                    Find quick answers to common questions about TaxMate
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="w-full">
                    {faqs.map((faq, index) => (
                      <AccordionItem key={index} value={`item-${index}`}>
                        <AccordionTrigger className="text-left font-semibold text-gray-900 hover:text-blue-900">
                          {faq.question}
                        </AccordionTrigger>
                        <AccordionContent className="text-gray-600 leading-relaxed">
                          {faq.answer}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardContent>
              </Card>

              <div className="mt-6 bg-gradient-to-br from-blue-50 to-green-50 rounded-lg p-8 border-2 border-blue-900">
                <h3 className="text-2xl font-bold text-gray-900 mb-3">
                  Still have questions?
                </h3>
                <p className="text-gray-600 mb-6">
                  Our AI chat assistant is available 24/7 to help answer your questions
                  and guide you through the tax filing process.
                </p>
                <a href="/dashboard">
                  <Button className="w-full bg-blue-900 hover:bg-blue-800">
                    Chat with TaxMate AI
                  </Button>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
