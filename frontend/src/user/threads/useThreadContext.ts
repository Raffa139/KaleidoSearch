import { useContext } from "react";
import { ThreadContext, type ThreadContextProps } from "./ThreadContext";
import type { Product, QueryEvaluation, UserAnswer } from "../../client/types";
import { client } from "../../client/kaleidoClient";

interface UseThreadContext {
  (): {
    isBusy: boolean;
    rerank: boolean;
    setRerank: (rerank: boolean) => void;
    getRecommendations: typeof client.Users.Threads.getRecommendations;
    postToThread: typeof client.Users.Threads.post;
    createThread: typeof client.Users.Threads.create;
  };
}

export const useThreadContext: UseThreadContext = () => {
  const { isBusy, setBusy, rerank, setRerank } = useContext(ThreadContext) as ThreadContextProps;

  const getRecommendations = async (tid: number): Promise<Product[]> => {
    setBusy(true);

    try {
      const response = await client.Users.Threads.getRecommendations(tid, rerank);
      setBusy(false);
      return response;
    } catch (error) {
      // TODO: Display that search needs refinement
      setBusy(false);
      return [];
    }
  };

  const postToThread = async (tid: number, content: { query?: string, answers?: UserAnswer[] }): Promise<QueryEvaluation> => {
    setBusy(true);
    const response = await client.Users.Threads.post(tid, content);
    setBusy(false);
    return response;
  };

  const createThread = async (query?: string): Promise<QueryEvaluation> => {
    setBusy(true);
    const response = await client.Users.Threads.create(query);
    setBusy(false);
    return response;
  };

  return { isBusy, rerank, setRerank, getRecommendations, postToThread, createThread };
};
