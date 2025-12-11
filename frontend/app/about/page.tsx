import { Card, CardContent } from '@/components/ui/card';
import { Target, Users, Lightbulb, Code2 } from 'lucide-react';

export default function About() {
  const techStack = [
    { name: 'Python', category: 'Backend' },
    { name: 'React', category: 'Frontend' },
    { name: 'Next.js', category: 'Framework' },
    { name: 'FastAPI', category: 'API' },
    { name: 'MongoDB', category: 'Database' },
    { name: 'Llama2', category: 'AI Model' },
    { name: 'FAISS', category: 'Vector DB' },
    { name: 'Cohere', category: 'NLP' },
    { name: 'TailwindCSS', category: 'Styling' },
    { name: 'TypeScript', category: 'Language' },
  ];

  return (
    <div className="pt-16">
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            About TaxMate
          </h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Revolutionizing tax filing through artificial intelligence and automation
          </p>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Mission</h2>
            <p className="text-xl text-gray-600 leading-relaxed">
              To make tax filing effortless using AI. We believe that everyone deserves
              a simple, accurate, and stress-free tax filing experience. By leveraging
              cutting-edge artificial intelligence and multi-agent systems, TaxMate
              transforms the traditionally complex process of tax preparation into
              an intuitive, automated workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            <Card className="border-2 border-blue-900">
              <CardContent className="pt-6">
                <div className="w-14 h-14 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Target className="h-8 w-8 text-blue-900" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">Our Vision</h3>
                <p className="text-gray-600 leading-relaxed">
                  To become India's most trusted AI-powered tax filing platform,
                  helping millions of taxpayers save time and maximize their refunds
                  through intelligent automation.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-600">
              <CardContent className="pt-6">
                <div className="w-14 h-14 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Lightbulb className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">Innovation</h3>
                <p className="text-gray-600 leading-relaxed">
                  We combine machine learning, natural language processing, and
                  intelligent document analysis to create a seamless tax filing
                  experience that learns and improves with every use.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Developed as Research Project
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              TaxMate was developed as a student research project exploring the
              intersection of artificial intelligence and financial automation.
              Our team is passionate about using technology to solve real-world
              problems and make complex systems more accessible.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <Card className="border-2 hover:border-blue-900 transition-all">
              <CardContent className="pt-6 text-center">
                <Users className="h-12 w-12 text-blue-900 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">Research Focus</h3>
                <p className="text-gray-600">
                  Multi-agent AI systems for document processing and decision-making
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-blue-900 transition-all">
              <CardContent className="pt-6 text-center">
                <Code2 className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">Technology</h3>
                <p className="text-gray-600">
                  Advanced NLP and machine learning for intelligent automation
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-blue-900 transition-all">
              <CardContent className="pt-6 text-center">
                <Target className="h-12 w-12 text-blue-900 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">Goal</h3>
                <p className="text-gray-600">
                  Making financial compliance accessible through AI innovation
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Technology Stack
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Built with modern technologies and frameworks to ensure reliability,
              security, and performance
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
            {techStack.map((tech, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-blue-50 to-white border-2 border-gray-200 rounded-lg p-4 text-center hover:border-blue-900 transition-all hover:shadow-lg group"
              >
                <div className="font-bold text-gray-900 mb-1 group-hover:text-blue-900 transition-colors">
                  {tech.name}
                </div>
                <div className="text-sm text-gray-600">{tech.category}</div>
              </div>
            ))}
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-green-50 rounded-2xl p-8 border-2 border-blue-900">
            <div className="max-w-3xl mx-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
                Key Technical Features
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Multi-Agent Architecture</h4>
                  <p className="text-sm text-gray-600">
                    Specialized AI agents handle different tasks like document parsing,
                    validation, and computation in parallel for efficiency.
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Vector Database</h4>
                  <p className="text-sm text-gray-600">
                    FAISS-powered semantic search enables intelligent document
                    retrieval and contextual understanding.
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Large Language Models</h4>
                  <p className="text-sm text-gray-600">
                    Llama2 and Cohere models provide natural language understanding
                    and generation capabilities.
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Real-Time Processing</h4>
                  <p className="text-sm text-gray-600">
                    FastAPI backend ensures lightning-fast document processing
                    and instant tax calculations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gradient-to-br from-blue-900 to-blue-800 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Join Our Journey
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            We're continuously improving TaxMate with new features and capabilities.
            Your feedback helps us build better tools for everyone.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/contact"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-blue-900 bg-white rounded-lg hover:bg-gray-100 transition-colors"
            >
              Get In Touch
            </a>
            <a
              href="/dashboard"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white border-2 border-white rounded-lg hover:bg-white hover:text-blue-900 transition-colors"
            >
              Try TaxMate Now
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
