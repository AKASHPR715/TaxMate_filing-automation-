import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle, CheckCircle, Save, FileText, Loader2 } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";

interface FilingViewerProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    itrType?: string; // e.g. "ITR-1"
}

interface MissingField {
    label: string;
    current_value: any;
    proxy_value: any;
    json_path: string;
    profile_value?: any;
}

interface UserProfile {
    [key: string]: any;
}

export function FilingViewer({ open, onOpenChange, itrType = "ITR1" }: FilingViewerProps) {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<any>(null);
    const [missingFields, setMissingFields] = useState<MissingField[]>([]);
    const [profile, setProfile] = useState<UserProfile>({});
    const [formValues, setFormValues] = useState<Record<string, string>>({});
    const [activeTab, setActiveTab] = useState("missing");

    // Fetch data when dialog opens
    useEffect(() => {
        if (open) {
            fetchFilingData();
        }
    }, [open, itrType]);

    const fetchFilingData = async () => {
        setLoading(true);
        try {
            // Clean ITR type if needed
            const type = itrType.replace("-", "");
            const res = await fetch(`http://localhost:8000/api/filing/latest/${type}`);
            if (!res.ok) throw new Error("Failed to fetch filing data");

            const result = await res.json();
            setData(result.data);
            setMissingFields(result.missing_fields || []);
            setProfile(result.user_profile || {});

            // Initialize form values from profile or missing fields
            const initialValues: Record<string, string> = {};
            (result.missing_fields || []).forEach((field: MissingField) => {
                // Prefill with profile value if exists, else empty
                initialValues[field.label] = field.profile_value ? String(field.profile_value) : "";
            });
            setFormValues(initialValues);

        } catch (e) {
            console.error(e);
            // Handle error (maybe show toast)
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (key: string, value: string) => {
        setFormValues(prev => ({ ...prev, [key]: value }));
    };

    const handleSave = async () => {
        setLoading(true);
        try {
            const updates: Record<string, any> = {};

            // Only send values that are not empty
            Object.entries(formValues).forEach(([key, value]) => {
                if (value && value.trim() !== "") {
                    updates[key] = value;
                }
            });

            if (Object.keys(updates).length === 0) {
                setLoading(false);
                return;
            }

            const res = await fetch("http://localhost:8000/api/filing/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ updates })
            });

            if (!res.ok) throw new Error("Update failed");

            // Refresh data
            await fetchFilingData();

            // Switch to full view to show updates? Or stay here?
            // Stay here for now

        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle>ITR Filing Data Review</DialogTitle>
                    <DialogDescription>
                        Review the generated ITR JSON and provide missing details.
                    </DialogDescription>
                </DialogHeader>

                {loading && !data ? (
                    <div className="flex justify-center items-center h-64">
                        <Loader2 className="h-8 w-8 animate-spin text-blue-900" />
                    </div>
                ) : (
                    <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="missing" className="relative">
                                Missing Details
                                {missingFields.length > 0 && (
                                    <span className="ml-2 bg-red-100 text-red-600 px-2 py-0.5 rounded-full text-xs font-bold">
                                        {missingFields.length}
                                    </span>
                                )}
                            </TabsTrigger>
                            <TabsTrigger value="full">Full JSON View</TabsTrigger>
                        </TabsList>

                        <TabsContent value="missing" className="flex-1 overflow-y-auto p-4 space-y-4">
                            {missingFields.length === 0 ? (
                                <div className="flex flex-col items-center justify-center h-48 text-center space-y-3">
                                    <CheckCircle className="h-12 w-12 text-green-500" />
                                    <p className="text-lg font-medium text-gray-900">All set!</p>
                                    <p className="text-sm text-gray-500">
                                        No missing values detected based on our checks.
                                    </p>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start space-x-3">
                                        <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                                        <div>
                                            <h4 className="font-medium text-yellow-900">Action Required</h4>
                                            <p className="text-sm text-yellow-800">
                                                Some fields in your ITR file contain placeholder values. Please update them below.
                                                These values will be saved to your profile for future filings.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="grid gap-4">
                                        {missingFields.map((field) => (
                                            <Card key={field.label}>
                                                <CardContent className="p-4 flex items-center gap-4">
                                                    <div className="flex-1">
                                                        <Label htmlFor={field.label} className="capitalize mb-1 block font-semibold">
                                                            {field.label.replace(/_/g, " ")}
                                                        </Label>
                                                        <p className="text-xs text-gray-500 font-mono mb-2 truncate" title={field.json_path}>
                                                            {field.json_path}
                                                        </p>
                                                        <div className="flex items-center gap-2 text-xs text-gray-400">
                                                            <span>Current: </span>
                                                            <code className="bg-gray-100 px-1 py-0.5 rounded text-gray-600">
                                                                {String(field.current_value)}
                                                            </code>
                                                        </div>
                                                    </div>
                                                    <div className="w-1/2">
                                                        <Input
                                                            id={field.label}
                                                            placeholder={`Enter ${field.label.replace(/_/g, " ")}`}
                                                            value={formValues[field.label] || ""}
                                                            onChange={(e) => handleInputChange(field.label, e.target.value)}
                                                            className="border-blue-200 focus:ring-blue-900"
                                                        />
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </TabsContent>

                        <TabsContent value="full" className="flex-1 overflow-hidden flex flex-col">
                            <div className="flex-1 border rounded-md bg-gray-50 overflow-auto p-4 font-mono text-xs">
                                <pre>{JSON.stringify(data, null, 2)}</pre>
                            </div>
                        </TabsContent>
                    </Tabs>
                )}

                <DialogFooter className="mt-4 pt-2 border-t">
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        Close
                    </Button>
                    {activeTab === "missing" && missingFields.length > 0 && (
                        <Button onClick={handleSave} disabled={loading} className="bg-blue-900 hover:bg-blue-800">
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save className="mr-2 h-4 w-4" />
                                    Save & Update
                                </>
                            )}
                        </Button>
                    )}
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
