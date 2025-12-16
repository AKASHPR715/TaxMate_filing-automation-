import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export type Database = {
  public: {
    Tables: {
      documents: {
        Row: {
          id: string;
          user_id: string;
          file_name: string;
          file_type: string;
          file_url: string;
          status: 'pending' | 'processing' | 'completed' | 'failed';
          extracted_data: any;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          file_name: string;
          file_type: string;
          file_url: string;
          status?: 'pending' | 'processing' | 'completed' | 'failed';
          extracted_data?: any;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          file_name?: string;
          file_type?: string;
          file_url?: string;
          status?: 'pending' | 'processing' | 'completed' | 'failed';
          extracted_data?: any;
          created_at?: string;
          updated_at?: string;
        };
      };
      tax_computations: {
        Row: {
          id: string;
          user_id: string;
          assessment_year: string;
          total_income: number;
          total_deductions: number;
          taxable_income: number;
          tax_liability: number;
          computation_data: any;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          assessment_year: string;
          total_income: number;
          total_deductions: number;
          taxable_income: number;
          tax_liability: number;
          computation_data?: any;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          assessment_year?: string;
          total_income?: number;
          total_deductions?: number;
          taxable_income?: number;
          tax_liability?: number;
          computation_data?: any;
          created_at?: string;
          updated_at?: string;
        };
      };
    };
  };
};
