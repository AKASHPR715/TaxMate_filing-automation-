import Link from 'next/link';
import { FileText, Mail, Shield } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <FileText className="h-8 w-8 text-blue-900" />
              <span className="text-2xl font-bold text-blue-900">TaxMate</span>
            </div>
            <p className="text-gray-600 max-w-md">
              Automate your tax filing with AI-powered intelligence.
              Making tax season effortless for everyone.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-gray-600 hover:text-blue-900 transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-600 hover:text-blue-900 transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-gray-600 hover:text-blue-900 transition-colors">
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/how-it-works" className="text-gray-600 hover:text-blue-900 transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link href="/features" className="text-gray-600 hover:text-blue-900 transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-gray-600 hover:text-blue-900 transition-colors">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-500 text-sm">
              © {new Date().getFullYear()} TaxMate. All rights reserved.
            </p>
            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Shield className="h-4 w-4" />
                <span>Secure & Encrypted</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Mail className="h-4 w-4" />
                <span>support@taxmate.ai</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
