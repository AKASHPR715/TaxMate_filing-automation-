
import { useState, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

interface ReviewDataFormProps {
    data: any;
    onUpdate: (newData: any) => void;
}

export function ReviewDataForm({ data, onUpdate }: ReviewDataFormProps) {
    const [localData, setLocalData] = useState(data);

    useEffect(() => {
        setLocalData(data);
    }, [data]);

    const handleChange = (sectionKey: string, path: string[], value: any) => {
        const newData = { ...localData };

        // Navigate to the nested object
        let current = newData[sectionKey];
        for (let i = 0; i < path.length - 1; i++) {
            if (!current[path[i]]) current[path[i]] = {};
            current = current[path[i]];
        }

        // Update value
        // Handle number conversion if the original was a number
        const lastKey = path[path.length - 1];
        if (typeof current[lastKey] === 'number') {
            current[lastKey] = parseFloat(value) || 0;
        } else {
            current[lastKey] = value;
        }

        setLocalData(newData);
        onUpdate(newData);
    };

    // Helper to find relevant keys
    const findKey = (keyword: string) => Object.keys(localData).find(k => k.toLowerCase().includes(keyword.toLowerCase()));

    const partAKey = findKey("Part_A");
    const partBKey = findKey("Part_B");
    const aisKey = findKey("AIS");

    return (
        <div className="h-full flex flex-col">
            <Tabs defaultValue="part-b" className="w-full h-full flex flex-col">
                <TabsList className="grid w-full grid-cols-3 mb-4">
                    <TabsTrigger value="part-a">Part A (Employer)</TabsTrigger>
                    <TabsTrigger value="part-b">Part B (Income & Deductions)</TabsTrigger>
                    <TabsTrigger value="ais">AIS (Other Income)</TabsTrigger>
                </TabsList>

                <style>{`
                    .custom-scrollbar::-webkit-scrollbar {
                        width: 12px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-track {
                        background: #f1f1f1; 
                        border-radius: 4px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb {
                        background: #888; 
                        border-radius: 6px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                        background: #555; 
                    }
                `}</style>

                <div className="flex-1 overflow-y-scroll min-h-0 custom-scrollbar border rounded-md p-2 bg-gray-50/50">
                    {/* PART A TAB */}
                    <TabsContent value="part-a" className="space-y-4">
                        {partAKey && localData[partAKey] ? (
                            <div className="space-y-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">Employer Details</CardTitle>
                                    </CardHeader>
                                    <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>Employer Name</Label>
                                            <Input
                                                value={localData[partAKey].employer_details?.name || ''}
                                                onChange={(e) => handleChange(partAKey, ['employer_details', 'name'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Employer PAN</Label>
                                            <Input
                                                value={localData[partAKey].employer_details?.PAN || ''}
                                                onChange={(e) => handleChange(partAKey, ['employer_details', 'PAN'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Employer TAN</Label>
                                            <Input
                                                value={localData[partAKey].employer_details?.TAN || ''}
                                                onChange={(e) => handleChange(partAKey, ['employer_details', 'TAN'], e.target.value)}
                                            />
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">TDS Summary</CardTitle>
                                    </CardHeader>
                                    <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="space-y-2">
                                            <Label>Total Amount Paid</Label>
                                            <Input
                                                type="number"
                                                value={localData[partAKey].tds_totals?.total_amount_paid || 0}
                                                onChange={(e) => handleChange(partAKey, ['tds_totals', 'total_amount_paid'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Total Tax Deducted</Label>
                                            <Input
                                                type="number"
                                                value={localData[partAKey].tds_totals?.total_tax_deducted || 0}
                                                onChange={(e) => handleChange(partAKey, ['tds_totals', 'total_tax_deducted'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Total Tax Deposited</Label>
                                            <Input
                                                type="number"
                                                value={localData[partAKey].tds_totals?.total_tax_deposited || 0}
                                                onChange={(e) => handleChange(partAKey, ['tds_totals', 'total_tax_deposited'], e.target.value)}
                                            />
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        ) : (
                            <div className="text-center p-8 text-gray-500">No Form 16 Part A data found.</div>
                        )}
                    </TabsContent>

                    {/* PART B TAB */}
                    <TabsContent value="part-b" className="space-y-4">
                        {partBKey && localData[partBKey] ? (
                            <div className="space-y-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">Salary Details</CardTitle>
                                    </CardHeader>
                                    <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>Gross Salary (Sec 17(1))</Label>
                                            <Input
                                                type="number"
                                                value={localData[partBKey].salary_details?.salary_u_s_17_1_a || 0}
                                                onChange={(e) => handleChange(partBKey, ['salary_details', 'salary_u_s_17_1_a'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Perquisites (Sec 17(2))</Label>
                                            <Input
                                                type="number"
                                                value={localData[partBKey].salary_details?.perquisites_u_s_17_2 || 0}
                                                onChange={(e) => handleChange(partBKey, ['salary_details', 'perquisites_u_s_17_2'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Standard Deduction</Label>
                                            <Input
                                                type="number"
                                                value={localData[partBKey].deductions_u_s_16?.standard_deduction || 0}
                                                onChange={(e) => handleChange(partBKey, ['deductions_u_s_16', 'standard_deduction'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Professional Tax</Label>
                                            <Input
                                                type="number"
                                                value={localData[partBKey].deductions_u_s_16?.professional_tax || 0}
                                                onChange={(e) => handleChange(partBKey, ['deductions_u_s_16', 'professional_tax'], e.target.value)}
                                            />
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">Chapter VI-A Deductions</CardTitle>
                                    </CardHeader>
                                    <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>Section 80C (Life Insurance, PPF, etc.)</Label>
                                            <Input
                                                type="number"
                                                value={localData[partBKey].deductions_chapter_VIA?.section_80C || 0}
                                                onChange={(e) => handleChange(partBKey, ['deductions_chapter_VIA', 'section_80C'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Section 80D (Health Insurance)</Label>
                                            <Input
                                                type="number"
                                                value={localData[partBKey].deductions_chapter_VIA?.section_80D || 0}
                                                onChange={(e) => handleChange(partBKey, ['deductions_chapter_VIA', 'section_80D'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Section 80CCD(1B) (NPS)</Label>
                                            <Input
                                                type="number"
                                                value={localData[partBKey].deductions_chapter_VIA?.section_80CCD_1B || 0}
                                                onChange={(e) => handleChange(partBKey, ['deductions_chapter_VIA', 'section_80CCD_1B'], e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Total Chapter VI-A Deductions</Label>
                                            <Input
                                                type="number"
                                                // This is usually a calculated field but providing edit access if user wants to override
                                                value={localData[partBKey].deductions_chapter_VIA?.total_deductions || 0}
                                                onChange={(e) => handleChange(partBKey, ['deductions_chapter_VIA', 'total_deductions'], e.target.value)}
                                            />
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        ) : (
                            <div className="text-center p-8 text-gray-500">No Form 16 Part B data found.</div>
                        )}
                    </TabsContent>

                    {/* AIS TAB */}
                    <TabsContent value="ais" className="space-y-4">
                        {aisKey && localData[aisKey] ? (
                            <div className="space-y-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">Other Income Details</CardTitle>
                                    </CardHeader>
                                    <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {/* Assuming structure based on Part B's other_income_reported field if AIS data is complex, 
                                     but looking at extracted files, AIS data might have its own structure. 
                                     The form16b other_income is what usually matters.
                                     Let's also look at Form 16B other income.
                                 */}
                                        {partBKey && localData[partBKey] ? (
                                            <>
                                                <div className="space-y-2">
                                                    <Label>Income from House Property</Label>
                                                    <Input
                                                        type="number"
                                                        value={localData[partBKey]?.other_income_reported?.house_property_income || 0}
                                                        onChange={(e) => handleChange(partBKey, ['other_income_reported', 'house_property_income'], e.target.value)}
                                                    />
                                                    <p className="text-xs text-muted-foreground">From Form 16 Part B</p>
                                                </div>
                                                <div className="space-y-2">
                                                    <Label>Income from Other Sources</Label>
                                                    <Input
                                                        type="number"
                                                        value={localData[partBKey]?.other_income_reported?.other_sources_income || 0}
                                                        onChange={(e) => handleChange(partBKey, ['other_income_reported', 'other_sources_income'], e.target.value)}
                                                    />
                                                    <p className="text-xs text-muted-foreground">From Form 16 Part B</p>
                                                </div>
                                            </>
                                        ) : (
                                            <p className="text-sm text-gray-500">Other income details from Form 16 Part B not available.</p>
                                        )}
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">AIS Raw Data Preview</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="bg-muted p-4 rounded-md overflow-x-auto">
                                            <pre className="text-xs">{JSON.stringify(localData[aisKey], null, 2)}</pre>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        ) : (
                            <div className="text-center p-8 text-gray-500">No AIS data found.</div>
                        )}
                    </TabsContent>
                </div>
            </Tabs>
        </div>
    );
}
