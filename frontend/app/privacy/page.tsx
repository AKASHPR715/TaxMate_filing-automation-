import { Card, CardContent } from '@/components/ui/card';
import { Shield, Lock, Eye, Database, FileCheck, AlertCircle } from 'lucide-react';

export default function Privacy() {
  return (
    <div className="pt-16">
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Shield className="h-16 w-16 mx-auto mb-6" />
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Privacy Policy
          </h1>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Your privacy and data security are our top priorities
          </p>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-blue-50 border-2 border-blue-900 rounded-lg p-6 mb-8">
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-6 w-6 text-blue-900 mt-1 flex-shrink-0" />
              <div>
                <p className="text-gray-900 font-semibold mb-2">Last Updated: October 2025</p>
                <p className="text-gray-700">
                  This privacy policy outlines how TaxMate collects, uses, and protects your
                  personal and financial information when you use our service.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-8">
            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Database className="h-6 w-6 text-blue-900" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">Information We Collect</h2>
                </div>
                <div className="space-y-4 text-gray-700">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Personal Information</h3>
                    <ul className="list-disc list-inside space-y-1 ml-2">
                      <li>Name, email address, and contact details</li>
                      <li>PAN number and other tax identifiers</li>
                      <li>Employment and income information</li>
                      <li>Bank account details for refund processing</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Document Data</h3>
                    <ul className="list-disc list-inside space-y-1 ml-2">
                      <li>Tax documents including Form 16, salary slips, investment proofs</li>
                      <li>Bank statements and transaction records</li>
                      <li>Property documents and loan certificates</li>
                      <li>Any other documents you upload for tax filing</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Usage Information</h3>
                    <ul className="list-disc list-inside space-y-1 ml-2">
                      <li>How you interact with our platform</li>
                      <li>Device information and IP addresses</li>
                      <li>Browser type and operating system</li>
                      <li>Pages visited and features used</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <FileCheck className="h-6 w-6 text-green-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">How We Use Your Information</h2>
                </div>
                <div className="space-y-3 text-gray-700">
                  <p>We use the information we collect to:</p>
                  <ul className="list-disc list-inside space-y-2 ml-2">
                    <li>Process your tax documents and compute your tax liability</li>
                    <li>Identify eligible deductions and exemptions</li>
                    <li>Generate and file your income tax return</li>
                    <li>Provide customer support and answer your questions</li>
                    <li>Improve our AI models and service quality</li>
                    <li>Send you important updates about your tax filing</li>
                    <li>Comply with legal and regulatory requirements</li>
                    <li>Detect and prevent fraud or unauthorized access</li>
                  </ul>
                  <p className="pt-2 font-semibold text-gray-900">
                    We will never use your information for marketing purposes without your explicit consent.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-600">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Lock className="h-6 w-6 text-green-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">Data Security</h2>
                </div>
                <div className="space-y-4 text-gray-700">
                  <p>
                    We implement industry-leading security measures to protect your sensitive information:
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <h4 className="font-semibold text-gray-900 mb-2">Encryption</h4>
                      <p className="text-sm">
                        All data is encrypted using 256-bit SSL/TLS encryption during transmission
                        and AES-256 encryption at rest.
                      </p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <h4 className="font-semibold text-gray-900 mb-2">Secure Storage</h4>
                      <p className="text-sm">
                        Documents are stored in secure, encrypted cloud servers with restricted access
                        and regular security audits.
                      </p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <h4 className="font-semibold text-gray-900 mb-2">Access Controls</h4>
                      <p className="text-sm">
                        Strict access controls ensure only authorized personnel can access your data,
                        and all access is logged.
                      </p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <h4 className="font-semibold text-gray-900 mb-2">Regular Backups</h4>
                      <p className="text-sm">
                        Your data is regularly backed up to prevent loss, and backups are also encrypted
                        and secured.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Eye className="h-6 w-6 text-blue-900" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">Data Sharing and Disclosure</h2>
                </div>
                <div className="space-y-3 text-gray-700">
                  <p className="font-semibold text-gray-900">
                    We do NOT sell, rent, or trade your personal information to third parties.
                  </p>
                  <p>We may share your information only in the following limited circumstances:</p>
                  <ul className="list-disc list-inside space-y-2 ml-2">
                    <li>
                      <strong>Government Authorities:</strong> When required by law or to comply with
                      tax filing regulations with the Income Tax Department
                    </li>
                    <li>
                      <strong>Service Providers:</strong> With trusted third-party service providers
                      who assist in operating our platform (under strict confidentiality agreements)
                    </li>
                    <li>
                      <strong>Legal Requirements:</strong> To respond to legal processes, enforce our
                      terms, or protect rights and safety
                    </li>
                    <li>
                      <strong>With Your Consent:</strong> When you explicitly authorize us to share
                      your information
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Shield className="h-6 w-6 text-blue-900" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">Your Rights</h2>
                </div>
                <div className="space-y-3 text-gray-700">
                  <p>You have the following rights regarding your personal information:</p>
                  <ul className="list-disc list-inside space-y-2 ml-2">
                    <li>
                      <strong>Access:</strong> Request a copy of all personal data we hold about you
                    </li>
                    <li>
                      <strong>Correction:</strong> Request correction of inaccurate or incomplete data
                    </li>
                    <li>
                      <strong>Deletion:</strong> Request deletion of your data (subject to legal retention requirements)
                    </li>
                    <li>
                      <strong>Portability:</strong> Request your data in a portable format
                    </li>
                    <li>
                      <strong>Withdrawal:</strong> Withdraw consent for data processing at any time
                    </li>
                    <li>
                      <strong>Objection:</strong> Object to processing of your data for certain purposes
                    </li>
                  </ul>
                  <p className="pt-3">
                    To exercise any of these rights, please contact us at{' '}
                    <a href="mailto:privacy@taxmate.ai" className="text-blue-900 hover:underline font-semibold">
                      privacy@taxmate.ai
                    </a>
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Data Retention</h2>
                <div className="space-y-3 text-gray-700">
                  <p>
                    We retain your personal information only for as long as necessary to fulfill the
                    purposes outlined in this privacy policy, unless a longer retention period is
                    required by law.
                  </p>
                  <ul className="list-disc list-inside space-y-2 ml-2">
                    <li>Tax documents and filings: Retained for 7 years as per Indian tax laws</li>
                    <li>Account information: Retained until you request deletion</li>
                    <li>Usage logs: Retained for 2 years for security and analytics</li>
                  </ul>
                  <p>
                    After the retention period, we securely delete or anonymize your data so it can
                    no longer be associated with you.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Cookies and Tracking</h2>
                <div className="space-y-3 text-gray-700">
                  <p>
                    We use cookies and similar tracking technologies to improve your experience on
                    our platform. Cookies help us:
                  </p>
                  <ul className="list-disc list-inside space-y-2 ml-2">
                    <li>Remember your preferences and settings</li>
                    <li>Understand how you use our service</li>
                    <li>Improve platform performance and security</li>
                    <li>Provide personalized features</li>
                  </ul>
                  <p>
                    You can control cookie settings through your browser preferences. However, disabling
                    cookies may affect some functionality of our service.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Children's Privacy</h2>
                <p className="text-gray-700">
                  TaxMate is not intended for use by individuals under the age of 18. We do not
                  knowingly collect personal information from children. If you believe we have
                  inadvertently collected information from a child, please contact us immediately.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Changes to This Policy</h2>
                <p className="text-gray-700">
                  We may update this privacy policy from time to time to reflect changes in our
                  practices or legal requirements. We will notify you of any material changes by
                  posting the new policy on this page and updating the "Last Updated" date. We
                  encourage you to review this policy periodically.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-blue-900 bg-blue-50">
              <CardContent className="pt-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Us</h2>
                <p className="text-gray-700 mb-4">
                  If you have any questions or concerns about this privacy policy or our data practices,
                  please contact us:
                </p>
                <div className="space-y-2 text-gray-900">
                  <p>
                    <strong>Email:</strong>{' '}
                    <a href="mailto:privacy@taxmate.ai" className="text-blue-900 hover:underline">
                      privacy@taxmate.ai
                    </a>
                  </p>
                  <p>
                    <strong>General Support:</strong>{' '}
                    <a href="mailto:support@taxmate.ai" className="text-blue-900 hover:underline">
                      support@taxmate.ai
                    </a>
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section className="py-12 bg-white border-t">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-600">
            TaxMate is committed to protecting your privacy and maintaining the security of your
            personal information. Thank you for trusting us with your tax filing needs.
          </p>
        </div>
      </section>
    </div>
  );
}
