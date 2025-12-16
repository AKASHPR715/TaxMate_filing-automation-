import { supabase } from './supabase';

export interface UploadDocumentParams {
  userId: string;
  file: File;
}

export interface DocumentResponse {
  id: string;
  fileName: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  extractedData?: any;
}

export interface TaxComputation {
  id: string;
  assessmentYear: string;
  totalIncome: number;
  totalDeductions: number;
  taxableIncome: number;
  taxLiability: number;
  computationData?: any;
}

export interface ChatMessage {
  message: string;
  response: string;
}

export class TaxMateAPI {
  private backendUrl: string;

  constructor(backendUrl?: string) {
    this.backendUrl = backendUrl || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  }

  async uploadDocument(params: UploadDocumentParams): Promise<DocumentResponse> {
    const { userId, file } = params;

    const fileExt = file.name.split('.').pop();
    const fileName = `${userId}/${Date.now()}.${fileExt}`;

    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('tax-documents')
      .upload(fileName, file);

    if (uploadError) {
      throw new Error(`Failed to upload file: ${uploadError.message}`);
    }

    const { data: urlData } = supabase.storage
      .from('tax-documents')
      .getPublicUrl(fileName);

    const { data: docData, error: docError } = await supabase
      .from('documents')
      .insert({
        user_id: userId,
        file_name: file.name,
        file_type: file.type,
        file_url: urlData.publicUrl,
        status: 'pending',
      })
      .select()
      .single();

    if (docError) {
      throw new Error(`Failed to create document record: ${docError.message}`);
    }

    this.processDocument(docData.id, urlData.publicUrl);

    return {
      id: docData.id,
      fileName: docData.file_name,
      status: docData.status,
    };
  }

  private async processDocument(documentId: string, fileUrl: string): Promise<void> {
    try {
      await supabase
        .from('documents')
        .update({ status: 'processing' })
        .eq('id', documentId);

      const response = await fetch(`${this.backendUrl}/api/process-document`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          file_url: fileUrl,
        }),
      });

      if (!response.ok) {
        throw new Error('Backend processing failed');
      }

      const result = await response.json();

      await supabase
        .from('documents')
        .update({
          status: 'completed',
          extracted_data: result.extracted_data,
        })
        .eq('id', documentId);
    } catch (error) {
      await supabase
        .from('documents')
        .update({ status: 'failed' })
        .eq('id', documentId);

      console.error('Document processing failed:', error);
    }
  }

  async getDocuments(userId: string): Promise<DocumentResponse[]> {
    const { data, error } = await supabase
      .from('documents')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error(`Failed to fetch documents: ${error.message}`);
    }

    return data.map((doc) => ({
      id: doc.id,
      fileName: doc.file_name,
      status: doc.status,
      extractedData: doc.extracted_data,
    }));
  }

  async computeTax(userId: string, assessmentYear: string): Promise<TaxComputation> {
    const response = await fetch(`${this.backendUrl}/api/compute-tax`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        assessment_year: assessmentYear,
      }),
    });

    if (!response.ok) {
      throw new Error('Tax computation failed');
    }

    const result = await response.json();

    const { data, error } = await supabase
      .from('tax_computations')
      .insert({
        user_id: userId,
        assessment_year: assessmentYear,
        total_income: result.total_income,
        total_deductions: result.total_deductions,
        taxable_income: result.taxable_income,
        tax_liability: result.tax_liability,
        computation_data: result.computation_data,
      })
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to save computation: ${error.message}`);
    }

    return {
      id: data.id,
      assessmentYear: data.assessment_year,
      totalIncome: data.total_income,
      totalDeductions: data.total_deductions,
      taxableIncome: data.taxable_income,
      taxLiability: data.tax_liability,
      computationData: data.computation_data,
    };
  }

  async getTaxComputation(userId: string, assessmentYear: string): Promise<TaxComputation | null> {
    const { data, error } = await supabase
      .from('tax_computations')
      .select('*')
      .eq('user_id', userId)
      .eq('assessment_year', assessmentYear)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    if (error) {
      throw new Error(`Failed to fetch computation: ${error.message}`);
    }

    if (!data) return null;

    return {
      id: data.id,
      assessmentYear: data.assessment_year,
      totalIncome: data.total_income,
      totalDeductions: data.total_deductions,
      taxableIncome: data.taxable_income,
      taxLiability: data.tax_liability,
      computationData: data.computation_data,
    };
  }

  async chatWithAI(userId: string, sessionId: string, message: string): Promise<string> {
    const response = await fetch(`${this.backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        session_id: sessionId,
        message,
      }),
    });

    if (!response.ok) {
      throw new Error('Chat request failed');
    }

    const result = await response.json();

    await supabase.from('chat_history').insert({
      user_id: userId,
      session_id: sessionId,
      message,
      response: result.response,
      context: result.context || {},
    });

    return result.response;
  }

  async getChatHistory(userId: string, sessionId: string): Promise<ChatMessage[]> {
    const { data, error } = await supabase
      .from('chat_history')
      .select('message, response')
      .eq('user_id', userId)
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true });

    if (error) {
      throw new Error(`Failed to fetch chat history: ${error.message}`);
    }

    return data;
  }

  async findDeductions(userId: string): Promise<any> {
    const response = await fetch(`${this.backendUrl}/api/find-deductions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error('Deduction analysis failed');
    }

    return await response.json();
  }

  async validateReturn(userId: string, assessmentYear: string): Promise<any> {
    const response = await fetch(`${this.backendUrl}/api/validate-return`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        assessment_year: assessmentYear,
      }),
    });

    if (!response.ok) {
      throw new Error('Return validation failed');
    }

    return await response.json();
  }
}

export const taxMateAPI = new TaxMateAPI();
