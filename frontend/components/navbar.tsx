'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Menu, X, FileText, LogIn, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AuthModal } from '@/components/auth-modal';
import { isAuthenticated, logout } from '@/lib/user';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsUserLoggedIn(isAuthenticated());
  }, []);

  const handleAuthSuccess = () => {
    setIsUserLoggedIn(true);
    router.push('/dashboard');
  };

  const handleLogout = () => {
    logout();
    setIsUserLoggedIn(false);
    router.push('/');
  };

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/how-it-works', label: 'How It Works' },
    { href: '/features', label: 'Features' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/about', label: 'About' },
    { href: '/contact', label: 'Contact' },
  ];

  return (
    <>
      <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-sm border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-2">
              <FileText className="h-8 w-8 text-blue-900" />
              <span className="text-2xl font-bold text-blue-900">TaxMate</span>
            </Link>

            <div className="hidden md:flex items-center space-x-8">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-gray-700 hover:text-blue-900 transition-colors font-medium"
                >
                  {link.label}
                </Link>
              ))}

              {!isUserLoggedIn ? (
                <Button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="bg-blue-900 hover:bg-blue-800"
                >
                  <LogIn className="mr-2 h-4 w-4" />
                  Login
                </Button>
              ) : (
                <Button
                  onClick={handleLogout}
                  variant="outline"
                  className="border-blue-900 text-blue-900 hover:bg-blue-50"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              )}
            </div>

            <button
              className="md:hidden"
              onClick={() => setIsOpen(!isOpen)}
              aria-label="Toggle menu"
            >
              {isOpen ? (
                <X className="h-6 w-6 text-gray-700" />
              ) : (
                <Menu className="h-6 w-6 text-gray-700" />
              )}
            </button>
          </div>
        </div>

        {isOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-4 space-y-3">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="block text-gray-700 hover:text-blue-900 transition-colors font-medium py-2"
                  onClick={() => setIsOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              {!isUserLoggedIn ? (
                <Button
                  onClick={() => {
                    setIsOpen(false);
                    setIsAuthModalOpen(true);
                  }}
                  className="w-full bg-blue-900 hover:bg-blue-800"
                >
                  <LogIn className="mr-2 h-4 w-4" />
                  Login
                </Button>
              ) : (
                <Button
                  onClick={() => {
                    setIsOpen(false);
                    handleLogout();
                  }}
                  variant="outline"
                  className="w-full border-blue-900 text-blue-900 hover:bg-blue-50"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              )}
            </div>
          </div>
        )}
      </nav>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  );
}
