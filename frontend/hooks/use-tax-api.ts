import { useState, useCallback } from 'react';
import { taxMateAPI, DocumentResponse, TaxComputation } from '@/lib/api';

export function useTaxAPI(userId: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadDocument = useCallback(async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const result = await taxMateAPI.uploadDocument({ userId, file });
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const getDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const docs = await taxMateAPI.getDocuments(userId);
      return docs;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch documents';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const computeTax = useCallback(async (assessmentYear: string) => {
    setLoading(true);
    setError(null);
    try {
      const computation = await taxMateAPI.computeTax(userId, assessmentYear);
      return computation;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Tax computation failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const getTaxComputation = useCallback(async (assessmentYear: string) => {
    setLoading(true);
    setError(null);
    try {
      const computation = await taxMateAPI.getTaxComputation(userId, assessmentYear);
      return computation;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch computation';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const chatWithAI = useCallback(async (sessionId: string, message: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await taxMateAPI.chatWithAI(userId, sessionId, message);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Chat request failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const getChatHistory = useCallback(async (sessionId: string) => {
    setLoading(true);
    setError(null);
    try {
      const history = await taxMateAPI.getChatHistory(userId, sessionId);
      return history;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch chat history';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const findDeductions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const deductions = await taxMateAPI.findDeductions(userId);
      return deductions;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Deduction analysis failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const validateReturn = useCallback(async (assessmentYear: string) => {
    setLoading(true);
    setError(null);
    try {
      const validation = await taxMateAPI.validateReturn(userId, assessmentYear);
      return validation;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Validation failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  return {
    loading,
    error,
    uploadDocument,
    getDocuments,
    computeTax,
    getTaxComputation,
    chatWithAI,
    getChatHistory,
    findDeductions,
    validateReturn,
  };
}
