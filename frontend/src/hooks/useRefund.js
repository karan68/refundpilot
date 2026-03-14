import { useState } from 'react';
import { submitRefund } from '../utils/api';

export function useRefund() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const submit = async (data) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await submitRefund(data);
      setResult(response.data);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit refund');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    setLoading(false);
  };

  return { submit, loading, result, error, reset };
}
