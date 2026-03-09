"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Building2, User, Calendar, FileText, IndianRupee, Landmark, TrendingDown } from "lucide-react";

interface ReviewDataFormProps {
    data: any;
    onUpdate: (newData: any) => void;
}

// Field component for consistent styling
const Field = ({
    label,
    value,
    onChange,
    type = "text",
    description
}: {
    label: string;
    value: any;
    onChange: (val: string) => void;
    type?: string;
    description?: string;
}) => (
    <div className="space-y-1.5">
        <Label className="text-sm font-medium">{label}</Label>
        <Input
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="h-9"
        />
        {description && <p className="text-xs text-muted-foreground">{description}</p>}
    </div>
);

// Currency field for displaying INR values
const CurrencyField = ({
    label,
    value,
    onChange,
    description
}: {
    label: string;
    value: number;
    onChange: (val: string) => void;
    description?: string;
}) => (
    <div className="space-y-1.5">
        <Label className="text-sm font-medium flex items-center gap-1">
            <IndianRupee className="h-3 w-3" />
            {label}
        </Label>
        <Input
            type="number"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="h-9"
        />
        {description && <p className="text-xs text-muted-foreground">{description}</p>}
    </div>
);

// Empty state component
const EmptyState = ({ message }: { message: string }) => (
    <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
        <AlertCircle className="h-10 w-10 mb-3 opacity-50" />
        <p className="font-medium">{message}</p>
        <p className="text-sm mt-1">Please ensure the document was uploaded correctly.</p>
    </div>
);

export function ReviewDataForm({ data, onUpdate }: ReviewDataFormProps) {
    const [localData, setLocalData] = useState(data);

    useEffect(() => {
        setLocalData(data);
    }, [data]);

    // Smart key detection that matches patterns like:
    // - "form16a_Form_16_Part_A_20251215_140618"
    // - "Form_16_Part_A"
    // - "Part_A"
    // - "form16a"
    const findFormKey = (patterns: string[]) => {
        const keys = Object.keys(localData || {});
        for (const pattern of patterns) {
            const found = keys.find(k =>
                k.toLowerCase().includes(pattern.toLowerCase())
            );
            if (found) return found;
        }
        return null;
    };

    // Find keys for each form type - order matters, more specific first
    const partAKey = findFormKey(["form16a", "part_a", "16_part_a", "16a"]);
    const partBKey = findFormKey(["form16b", "part_b", "16_part_b", "16b"]);
    const aisKey = findFormKey(["ais", "form_ais"]);

    const handleChange = (sectionKey: string, path: string[], value: any) => {
        const newData = JSON.parse(JSON.stringify(localData)); // Deep copy

        // Navigate to the nested object
        let current = newData[sectionKey];
        if (!current) {
            newData[sectionKey] = {};
            current = newData[sectionKey];
        }

        for (let i = 0; i < path.length - 1; i++) {
            if (!current[path[i]]) current[path[i]] = {};
            current = current[path[i]];
        }

        // Update value - handle number conversion
        const lastKey = path[path.length - 1];
        const originalValue = current[lastKey];
        if (typeof originalValue === 'number') {
            current[lastKey] = parseFloat(value) || 0;
        } else {
            current[lastKey] = value;
        }

        setLocalData(newData);
        onUpdate(newData);
    };

    // Helper to safely get nested values
    const getValue = (obj: any, path: string[], defaultValue: any = '') => {
        try {
            let current = obj;
            for (const key of path) {
                if (current === undefined || current === null) return defaultValue;
                current = current[key];
            }
            return current ?? defaultValue;
        } catch {
            return defaultValue;
        }
    };



    return (
        <div className="h-full flex flex-col">
            <Tabs defaultValue="part-a" className="w-full h-full flex flex-col">
                <TabsList className="grid w-full grid-cols-3 mb-4">
                    <TabsTrigger value="part-a" className="flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        Form 16A
                        {partAKey && <Badge variant="secondary" className="ml-1 h-5 text-xs">✓</Badge>}
                    </TabsTrigger>
                    <TabsTrigger value="part-b" className="flex items-center gap-1">
                        <IndianRupee className="h-4 w-4" />
                        Form 16B
                        {partBKey && <Badge variant="secondary" className="ml-1 h-5 text-xs">✓</Badge>}
                    </TabsTrigger>
                    <TabsTrigger value="ais" className="flex items-center gap-1">
                        <Landmark className="h-4 w-4" />
                        Form AIS
                        {aisKey && <Badge variant="secondary" className="ml-1 h-5 text-xs">✓</Badge>}
                    </TabsTrigger>
                </TabsList>

                <style>{`
                    .custom-scrollbar::-webkit-scrollbar {
                        width: 10px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-track {
                        background: #f1f1f1; 
                        border-radius: 4px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb {
                        background: #888; 
                        border-radius: 5px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                        background: #666; 
                    }
                `}</style>

                <div className="flex-1 overflow-y-auto min-h-0 custom-scrollbar border rounded-md p-3 bg-gray-50/50">

                    {/* ========== FORM 16 PART A TAB ========== */}
                    <TabsContent value="part-a" className="mt-0">
                        {partAKey && localData[partAKey] ? (
                            <Accordion type="multiple" defaultValue={["employer", "employee", "assessment", "tds"]} className="space-y-3">

                                {/* Employer Details */}
                                <AccordionItem value="employer" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <Building2 className="h-4 w-4 text-blue-600" />
                                            <span className="font-semibold">Employer Details</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <Field
                                                label="Employer Name"
                                                value={getValue(localData[partAKey], ['employer_details', 'name'])}
                                                onChange={(v) => handleChange(partAKey, ['employer_details', 'name'], v)}
                                            />
                                            <Field
                                                label="Employer PAN"
                                                value={getValue(localData[partAKey], ['employer_details', 'PAN'])}
                                                onChange={(v) => handleChange(partAKey, ['employer_details', 'PAN'], v)}
                                            />
                                            <Field
                                                label="Employer TAN"
                                                value={getValue(localData[partAKey], ['employer_details', 'TAN'])}
                                                onChange={(v) => handleChange(partAKey, ['employer_details', 'TAN'], v)}
                                            />
                                            <Field
                                                label="Contact Number"
                                                value={getValue(localData[partAKey], ['employer_details', 'contact_number'])}
                                                onChange={(v) => handleChange(partAKey, ['employer_details', 'contact_number'], v)}
                                            />
                                            <div className="md:col-span-2">
                                                <Field
                                                    label="Address"
                                                    value={getValue(localData[partAKey], ['employer_details', 'address'])}
                                                    onChange={(v) => handleChange(partAKey, ['employer_details', 'address'], v)}
                                                />
                                            </div>
                                            <Field
                                                label="Email"
                                                value={getValue(localData[partAKey], ['employer_details', 'email'])}
                                                onChange={(v) => handleChange(partAKey, ['employer_details', 'email'], v)}
                                            />
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Employee Details */}
                                <AccordionItem value="employee" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <User className="h-4 w-4 text-green-600" />
                                            <span className="font-semibold">Employee Details</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <Field
                                                label="Employee Name"
                                                value={getValue(localData[partAKey], ['employee_details', 'name'])}
                                                onChange={(v) => handleChange(partAKey, ['employee_details', 'name'], v)}
                                            />
                                            <Field
                                                label="Employee PAN"
                                                value={getValue(localData[partAKey], ['employee_details', 'PAN'])}
                                                onChange={(v) => handleChange(partAKey, ['employee_details', 'PAN'], v)}
                                            />
                                            <Field
                                                label="Reference Number"
                                                value={getValue(localData[partAKey], ['employee_details', 'employee_reference_no'])}
                                                onChange={(v) => handleChange(partAKey, ['employee_details', 'employee_reference_no'], v)}
                                            />
                                            <div className="md:col-span-2">
                                                <Field
                                                    label="Address"
                                                    value={getValue(localData[partAKey], ['employee_details', 'address'])}
                                                    onChange={(v) => handleChange(partAKey, ['employee_details', 'address'], v)}
                                                />
                                            </div>
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Assessment Details */}
                                <AccordionItem value="assessment" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <Calendar className="h-4 w-4 text-purple-600" />
                                            <span className="font-semibold">Assessment Details</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <Field
                                                label="Assessment Year"
                                                value={getValue(localData[partAKey], ['assessment_details', 'assessment_year'])}
                                                onChange={(v) => handleChange(partAKey, ['assessment_details', 'assessment_year'], v)}
                                            />
                                            <Field
                                                label="Period From"
                                                value={getValue(localData[partAKey], ['assessment_details', 'period_from'])}
                                                onChange={(v) => handleChange(partAKey, ['assessment_details', 'period_from'], v)}
                                            />
                                            <Field
                                                label="Period To"
                                                value={getValue(localData[partAKey], ['assessment_details', 'period_to'])}
                                                onChange={(v) => handleChange(partAKey, ['assessment_details', 'period_to'], v)}
                                            />
                                            <div className="md:col-span-3">
                                                <Field
                                                    label="CIT (TDS) Office"
                                                    value={getValue(localData[partAKey], ['assessment_details', 'CIT_TDS_office'])}
                                                    onChange={(v) => handleChange(partAKey, ['assessment_details', 'CIT_TDS_office'], v)}
                                                />
                                            </div>
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* TDS Summary */}
                                <AccordionItem value="tds" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <IndianRupee className="h-4 w-4 text-orange-600" />
                                            <span className="font-semibold">TDS Summary & Totals</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="space-y-4">
                                            {/* TDS Totals */}
                                            <Card className="bg-blue-50 border-blue-200">
                                                <CardHeader className="pb-2">
                                                    <CardTitle className="text-sm">TDS Totals</CardTitle>
                                                </CardHeader>
                                                <CardContent>
                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                        <CurrencyField
                                                            label="Total Amount Paid"
                                                            value={getValue(localData[partAKey], ['tds_totals', 'total_amount_paid'], 0)}
                                                            onChange={(v) => handleChange(partAKey, ['tds_totals', 'total_amount_paid'], v)}
                                                        />
                                                        <CurrencyField
                                                            label="Total Tax Deducted"
                                                            value={getValue(localData[partAKey], ['tds_totals', 'total_tax_deducted'], 0)}
                                                            onChange={(v) => handleChange(partAKey, ['tds_totals', 'total_tax_deducted'], v)}
                                                        />
                                                        <CurrencyField
                                                            label="Total Tax Deposited"
                                                            value={getValue(localData[partAKey], ['tds_totals', 'total_tax_deposited'], 0)}
                                                            onChange={(v) => handleChange(partAKey, ['tds_totals', 'total_tax_deposited'], v)}
                                                        />
                                                    </div>
                                                </CardContent>
                                            </Card>

                                            {/* Quarterly TDS Summary */}
                                            {getValue(localData[partAKey], ['tds_summary'], []).length > 0 && (
                                                <div className="space-y-2">
                                                    <h4 className="font-medium text-sm">Quarterly Breakdown</h4>
                                                    {getValue(localData[partAKey], ['tds_summary'], []).map((item: any, idx: number) => (
                                                        <Card key={idx} className="bg-gray-50">
                                                            <CardContent className="pt-4">
                                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                                                    <Field
                                                                        label={`Quarter`}
                                                                        value={item.quarter || ''}
                                                                        onChange={(v) => {
                                                                            const newData = JSON.parse(JSON.stringify(localData));
                                                                            newData[partAKey].tds_summary[idx].quarter = v;
                                                                            setLocalData(newData);
                                                                            onUpdate(newData);
                                                                        }}
                                                                    />
                                                                    <CurrencyField
                                                                        label="Amount Paid"
                                                                        value={item.amount_paid_credited || 0}
                                                                        onChange={(v) => {
                                                                            const newData = JSON.parse(JSON.stringify(localData));
                                                                            newData[partAKey].tds_summary[idx].amount_paid_credited = parseFloat(v) || 0;
                                                                            setLocalData(newData);
                                                                            onUpdate(newData);
                                                                        }}
                                                                    />
                                                                    <CurrencyField
                                                                        label="Tax Deducted"
                                                                        value={item.tax_deducted || 0}
                                                                        onChange={(v) => {
                                                                            const newData = JSON.parse(JSON.stringify(localData));
                                                                            newData[partAKey].tds_summary[idx].tax_deducted = parseFloat(v) || 0;
                                                                            setLocalData(newData);
                                                                            onUpdate(newData);
                                                                        }}
                                                                    />
                                                                    <CurrencyField
                                                                        label="Tax Deposited"
                                                                        value={item.tax_deposited || 0}
                                                                        onChange={(v) => {
                                                                            const newData = JSON.parse(JSON.stringify(localData));
                                                                            newData[partAKey].tds_summary[idx].tax_deposited = parseFloat(v) || 0;
                                                                            setLocalData(newData);
                                                                            onUpdate(newData);
                                                                        }}
                                                                    />
                                                                </div>
                                                            </CardContent>
                                                        </Card>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Certificate Details */}
                                <AccordionItem value="certificate" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <FileText className="h-4 w-4 text-teal-600" />
                                            <span className="font-semibold">Certificate Details</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <Field
                                                label="Certificate Number"
                                                value={getValue(localData[partAKey], ['certificate_details', 'certificate_number'])}
                                                onChange={(v) => handleChange(partAKey, ['certificate_details', 'certificate_number'], v)}
                                            />
                                            <Field
                                                label="Issue Date"
                                                value={getValue(localData[partAKey], ['certificate_details', 'issue_date'])}
                                                onChange={(v) => handleChange(partAKey, ['certificate_details', 'issue_date'], v)}
                                            />
                                            <Field
                                                label="Place"
                                                value={getValue(localData[partAKey], ['certificate_details', 'place'])}
                                                onChange={(v) => handleChange(partAKey, ['certificate_details', 'place'], v)}
                                            />
                                            <Field
                                                label="Signatory Name"
                                                value={getValue(localData[partAKey], ['certificate_details', 'signatory_name'])}
                                                onChange={(v) => handleChange(partAKey, ['certificate_details', 'signatory_name'], v)}
                                            />
                                            <Field
                                                label="Designation"
                                                value={getValue(localData[partAKey], ['certificate_details', 'designation'])}
                                                onChange={(v) => handleChange(partAKey, ['certificate_details', 'designation'], v)}
                                            />
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                            </Accordion>
                        ) : (
                            <EmptyState message="No Form 16 Part A data found" />
                        )}
                    </TabsContent>

                    {/* ========== FORM 16 PART B TAB ========== */}
                    <TabsContent value="part-b" className="mt-0">
                        {partBKey && localData[partBKey] ? (
                            <Accordion type="multiple" defaultValue={["salary", "exemptions", "deductions16", "tax"]} className="space-y-3">

                                {/* Salary Details */}
                                <AccordionItem value="salary" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <IndianRupee className="h-4 w-4 text-green-600" />
                                            <span className="font-semibold">Salary Details</span>
                                            <Badge variant="outline" className="ml-2">
                                                ₹{getValue(localData[partBKey], ['salary_details', 'total_salary'], 0).toLocaleString()}
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <CurrencyField
                                                label="Salary u/s 17(1)(a)"
                                                value={getValue(localData[partBKey], ['salary_details', 'salary_u_s_17_1_a'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['salary_details', 'salary_u_s_17_1_a'], v)}
                                                description="Basic salary component"
                                            />
                                            <CurrencyField
                                                label="Salary u/s 17(1)(b)"
                                                value={getValue(localData[partBKey], ['salary_details', 'salary_u_s_17_1_b'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['salary_details', 'salary_u_s_17_1_b'], v)}
                                                description="Value of perquisites"
                                            />
                                            <CurrencyField
                                                label="Salary u/s 17(3)"
                                                value={getValue(localData[partBKey], ['salary_details', 'salary_u_s_17_3'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['salary_details', 'salary_u_s_17_3'], v)}
                                                description="Profits in lieu of salary"
                                            />
                                            <CurrencyField
                                                label="Total Salary"
                                                value={getValue(localData[partBKey], ['salary_details', 'total_salary'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['salary_details', 'total_salary'], v)}
                                            />
                                            <CurrencyField
                                                label="Salary from Other Employers"
                                                value={getValue(localData[partBKey], ['salary_details', 'salary_from_other_employers'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['salary_details', 'salary_from_other_employers'], v)}
                                            />
                                            <CurrencyField
                                                label="Perquisites u/s 17(2)"
                                                value={getValue(localData[partBKey], ['salary_details', 'perquisites_u_s_17_2'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['salary_details', 'perquisites_u_s_17_2'], v)}
                                            />
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Exemptions u/s 10 */}
                                <AccordionItem value="exemptions" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <TrendingDown className="h-4 w-4 text-blue-600" />
                                            <span className="font-semibold">Exemptions u/s 10</span>
                                            <Badge variant="outline" className="ml-2">
                                                ₹{getValue(localData[partBKey], ['exemptions_u_s_10', 'total_exemptions'], 0).toLocaleString()}
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <CurrencyField
                                                label="Leave Travel Concession"
                                                value={getValue(localData[partBKey], ['exemptions_u_s_10', 'leave_travel_concession'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['exemptions_u_s_10', 'leave_travel_concession'], v)}
                                            />
                                            <CurrencyField
                                                label="Gratuity"
                                                value={getValue(localData[partBKey], ['exemptions_u_s_10', 'gratuity'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['exemptions_u_s_10', 'gratuity'], v)}
                                            />
                                            <CurrencyField
                                                label="Leave Encashment"
                                                value={getValue(localData[partBKey], ['exemptions_u_s_10', 'leave_encashment'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['exemptions_u_s_10', 'leave_encashment'], v)}
                                            />
                                            <CurrencyField
                                                label="House Rent Allowance"
                                                value={getValue(localData[partBKey], ['exemptions_u_s_10', 'house_rent_allowance'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['exemptions_u_s_10', 'house_rent_allowance'], v)}
                                            />
                                            <CurrencyField
                                                label="Commuted Pension"
                                                value={getValue(localData[partBKey], ['exemptions_u_s_10', 'commuted_pension'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['exemptions_u_s_10', 'commuted_pension'], v)}
                                            />
                                            <CurrencyField
                                                label="Other Exemptions"
                                                value={getValue(localData[partBKey], ['exemptions_u_s_10', 'any_other_exemption'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['exemptions_u_s_10', 'any_other_exemption'], v)}
                                            />
                                            <CurrencyField
                                                label="Total Exemptions"
                                                value={getValue(localData[partBKey], ['exemptions_u_s_10', 'total_exemptions'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['exemptions_u_s_10', 'total_exemptions'], v)}
                                            />
                                            <CurrencyField
                                                label="Net Salary After Exemptions"
                                                value={getValue(localData[partBKey], ['net_salary_after_exemptions'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['net_salary_after_exemptions'], v)}
                                            />
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Deductions u/s 16 */}
                                <AccordionItem value="deductions16" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <TrendingDown className="h-4 w-4 text-purple-600" />
                                            <span className="font-semibold">Deductions u/s 16</span>
                                            <Badge variant="outline" className="ml-2">
                                                ₹{getValue(localData[partBKey], ['deductions_u_s_16', 'total_deductions'], 0).toLocaleString()}
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <CurrencyField
                                                label="Standard Deduction"
                                                value={getValue(localData[partBKey], ['deductions_u_s_16', 'standard_deduction'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['deductions_u_s_16', 'standard_deduction'], v)}
                                                description="Max ₹50,000 for FY 2023-24"
                                            />
                                            <CurrencyField
                                                label="Entertainment Allowance"
                                                value={getValue(localData[partBKey], ['deductions_u_s_16', 'entertainment_allowance'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['deductions_u_s_16', 'entertainment_allowance'], v)}
                                            />
                                            <CurrencyField
                                                label="Professional Tax"
                                                value={getValue(localData[partBKey], ['deductions_u_s_16', 'professional_tax'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['deductions_u_s_16', 'professional_tax'], v)}
                                            />
                                            <CurrencyField
                                                label="Total Deductions u/s 16"
                                                value={getValue(localData[partBKey], ['deductions_u_s_16', 'total_deductions'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['deductions_u_s_16', 'total_deductions'], v)}
                                            />
                                        </div>
                                        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                                            <CurrencyField
                                                label="Income Chargeable Under Salary"
                                                value={getValue(localData[partBKey], ['income_chargeable_under_salary'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['income_chargeable_under_salary'], v)}
                                            />
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Other Income */}
                                <AccordionItem value="other_income" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <Landmark className="h-4 w-4 text-cyan-600" />
                                            <span className="font-semibold">Other Income Reported</span>
                                            <Badge variant="outline" className="ml-2">
                                                ₹{getValue(localData[partBKey], ['other_income_reported', 'total_other_income'], 0).toLocaleString()}
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <CurrencyField
                                                label="House Property Income"
                                                value={getValue(localData[partBKey], ['other_income_reported', 'house_property_income'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['other_income_reported', 'house_property_income'], v)}
                                                description="Can be negative (loss)"
                                            />
                                            <CurrencyField
                                                label="Other Sources Income"
                                                value={getValue(localData[partBKey], ['other_income_reported', 'other_sources_income'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['other_income_reported', 'other_sources_income'], v)}
                                            />
                                            <CurrencyField
                                                label="Total Other Income"
                                                value={getValue(localData[partBKey], ['other_income_reported', 'total_other_income'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['other_income_reported', 'total_other_income'], v)}
                                            />
                                            <CurrencyField
                                                label="Gross Total Income"
                                                value={getValue(localData[partBKey], ['gross_total_income'], 0)}
                                                onChange={(v) => handleChange(partBKey, ['gross_total_income'], v)}
                                            />
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>


                                {/* Tax Computation */}
                                <AccordionItem value="tax" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <IndianRupee className="h-4 w-4 text-red-600" />
                                            <span className="font-semibold">Tax Computation</span>
                                            <Badge className="ml-2 bg-red-100 text-red-800">
                                                ₹{getValue(localData[partBKey], ['tax_computation', 'total_tax_liability'], 0).toLocaleString()}
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="space-y-4">
                                            <div className="p-3 bg-yellow-50 rounded-lg">
                                                <CurrencyField
                                                    label="Taxable Income"
                                                    value={getValue(localData[partBKey], ['taxable_income'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['taxable_income'], v)}
                                                />
                                            </div>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <CurrencyField
                                                    label="Income Tax"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'income_tax'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'income_tax'], v)}
                                                />
                                                <CurrencyField
                                                    label="Surcharge"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'surcharge'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'surcharge'], v)}
                                                />
                                                <CurrencyField
                                                    label="Rebate u/s 87A"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'rebate_u_s_87A'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'rebate_u_s_87A'], v)}
                                                />
                                                <CurrencyField
                                                    label="Health & Education Cess"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'health_education_cess'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'health_education_cess'], v)}
                                                    description="4% of tax + surcharge"
                                                />
                                                <CurrencyField
                                                    label="Relief u/s 89"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'relief_u_s_89'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'relief_u_s_89'], v)}
                                                />
                                                <CurrencyField
                                                    label="Total Tax Liability"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'total_tax_liability'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'total_tax_liability'], v)}
                                                />
                                                <CurrencyField
                                                    label="TDS Deducted"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'tax_deducted_at_source'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'tax_deducted_at_source'], v)}
                                                />
                                                <CurrencyField
                                                    label="Net Tax Payable/Refundable"
                                                    value={getValue(localData[partBKey], ['tax_computation', 'net_tax_payable_or_refundable'], 0)}
                                                    onChange={(v) => handleChange(partBKey, ['tax_computation', 'net_tax_payable_or_refundable'], v)}
                                                />
                                            </div>
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                            </Accordion>
                        ) : (
                            <EmptyState message="No Form 16 Part B data found" />
                        )}
                    </TabsContent>

                    {/* ========== FORM AIS TAB ========== */}
                    <TabsContent value="ais" className="mt-0">
                        {aisKey && localData[aisKey] ? (
                            <Accordion type="multiple" defaultValue={["assessee", "interest", "dividend", "tds_tcs"]} className="space-y-3">

                                {/* Assessee Details */}
                                <AccordionItem value="assessee" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <User className="h-4 w-4 text-blue-600" />
                                            <span className="font-semibold">Assessee Details</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <Field
                                                label="PAN"
                                                value={getValue(localData[aisKey], ['assessee_details', 'PAN'])}
                                                onChange={(v) => handleChange(aisKey, ['assessee_details', 'PAN'], v)}
                                            />
                                            <Field
                                                label="Name"
                                                value={getValue(localData[aisKey], ['assessee_details', 'name'])}
                                                onChange={(v) => handleChange(aisKey, ['assessee_details', 'name'], v)}
                                            />
                                            <Field
                                                label="Assessment Year"
                                                value={getValue(localData[aisKey], ['assessee_details', 'assessment_year'])}
                                                onChange={(v) => handleChange(aisKey, ['assessee_details', 'assessment_year'], v)}
                                            />
                                            <Field
                                                label="Financial Year"
                                                value={getValue(localData[aisKey], ['assessee_details', 'financial_year'])}
                                                onChange={(v) => handleChange(aisKey, ['assessee_details', 'financial_year'], v)}
                                            />
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Interest Income */}
                                <AccordionItem value="interest" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <Landmark className="h-4 w-4 text-green-600" />
                                            <span className="font-semibold">Interest Income</span>
                                            <Badge variant="outline" className="ml-2">
                                                {getValue(localData[aisKey], ['interest_income'], []).length} entries
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        {getValue(localData[aisKey], ['interest_income'], []).length > 0 ? (
                                            <div className="space-y-3">
                                                {getValue(localData[aisKey], ['interest_income'], []).map((item: any, idx: number) => (
                                                    <Card key={idx} className="bg-gray-50">
                                                        <CardContent className="pt-4">
                                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                                <Field
                                                                    label="Source"
                                                                    value={item.source || ''}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].interest_income[idx].source = v;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                                <Field
                                                                    label="Bank/Entity"
                                                                    value={item.bank_or_entity_name || ''}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].interest_income[idx].bank_or_entity_name = v;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                                <CurrencyField
                                                                    label="Interest Amount"
                                                                    value={item.interest_amount || 0}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].interest_income[idx].interest_amount = parseFloat(v) || 0;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                            </div>
                                                        </CardContent>
                                                    </Card>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-center text-muted-foreground py-4">No interest income entries found in AIS</p>
                                        )}
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Dividend Income */}
                                <AccordionItem value="dividend" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <IndianRupee className="h-4 w-4 text-purple-600" />
                                            <span className="font-semibold">Dividend Income</span>
                                            <Badge variant="outline" className="ml-2">
                                                {getValue(localData[aisKey], ['dividend_income'], []).length} entries
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        {getValue(localData[aisKey], ['dividend_income'], []).length > 0 ? (
                                            <div className="space-y-3">
                                                {getValue(localData[aisKey], ['dividend_income'], []).map((item: any, idx: number) => (
                                                    <Card key={idx} className="bg-gray-50">
                                                        <CardContent className="pt-4">
                                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                                <Field
                                                                    label="Company Name"
                                                                    value={item.company_name || ''}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].dividend_income[idx].company_name = v;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                                <Field
                                                                    label="ISIN Code"
                                                                    value={item.isin_code || ''}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].dividend_income[idx].isin_code = v;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                                <CurrencyField
                                                                    label="Dividend Amount"
                                                                    value={item.dividend_amount || 0}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].dividend_income[idx].dividend_amount = parseFloat(v) || 0;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                            </div>
                                                        </CardContent>
                                                    </Card>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-center text-muted-foreground py-4">No dividend income entries found in AIS</p>
                                        )}
                                    </AccordionContent>
                                </AccordionItem>

                                {/* TDS/TCS Information */}
                                <AccordionItem value="tds_tcs" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <FileText className="h-4 w-4 text-orange-600" />
                                            <span className="font-semibold">TDS/TCS Information</span>
                                            <Badge variant="outline" className="ml-2">
                                                {getValue(localData[aisKey], ['tds_tcs_information'], []).length} entries
                                            </Badge>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        {getValue(localData[aisKey], ['tds_tcs_information'], []).length > 0 ? (
                                            <div className="space-y-3">
                                                {getValue(localData[aisKey], ['tds_tcs_information'], []).map((item: any, idx: number) => (
                                                    <Card key={idx} className="bg-gray-50">
                                                        <CardContent className="pt-4">
                                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                                <Field
                                                                    label="Source Type"
                                                                    value={item.source_type || ''}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].tds_tcs_information[idx].source_type = v;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                                <Field
                                                                    label="Deductor/Collector"
                                                                    value={item.deductor_collector_name || ''}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].tds_tcs_information[idx].deductor_collector_name = v;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                                <CurrencyField
                                                                    label="Amount Paid/Credited"
                                                                    value={item.amount_paid_credited || 0}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].tds_tcs_information[idx].amount_paid_credited = parseFloat(v) || 0;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                                <CurrencyField
                                                                    label="Tax Deducted/Collected"
                                                                    value={item.tax_deducted_collected || 0}
                                                                    onChange={(v) => {
                                                                        const newData = JSON.parse(JSON.stringify(localData));
                                                                        newData[aisKey].tds_tcs_information[idx].tax_deducted_collected = parseFloat(v) || 0;
                                                                        setLocalData(newData);
                                                                        onUpdate(newData);
                                                                    }}
                                                                />
                                                            </div>
                                                        </CardContent>
                                                    </Card>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-center text-muted-foreground py-4">No TDS/TCS information found in AIS</p>
                                        )}
                                    </AccordionContent>
                                </AccordionItem>

                                {/* Raw AIS Data Preview */}
                                <AccordionItem value="raw" className="border rounded-lg bg-white">
                                    <AccordionTrigger className="px-4 hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <FileText className="h-4 w-4 text-gray-600" />
                                            <span className="font-semibold">Full AIS Data (Read-only)</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="px-4 pb-4">
                                        <div className="bg-muted p-4 rounded-md overflow-x-auto max-h-[300px]">
                                            <pre className="text-xs">{JSON.stringify(localData[aisKey], null, 2)}</pre>
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                            </Accordion>
                        ) : (
                            <EmptyState message="No AIS data found" />
                        )}
                    </TabsContent>

                </div>
            </Tabs>
        </div>
    );
}
