import { useState, useEffect } from 'react';

type AsyncFunction<T> = (...args: any[]) => Promise<T>;

interface UseAPIReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: AsyncFunction<T>;
  refetch: () => void;
}

export const useAPI = <T>(
  asyncFunction: AsyncFunction<T>,
  immediate: boolean = true,
  ...args: any[]
): UseAPIReturn<T> => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<Error | null>(null);

  const execute = async (...newArgs: any[]): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      const result = await asyncFunction(...newArgs);
      setData(result);
      return result;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const refetch = () => {
    execute(...args);
  };

  useEffect(() => {
    if (immediate) {
      execute(...args);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return { data, loading, error, execute, refetch };
};
