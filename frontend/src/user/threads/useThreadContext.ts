import { useContext } from "react";
import { ThreadContext, type ThreadContextProps } from "./ThreadContext";
import type { Product, QueryEvaluation, UserAnswer } from "../../client/types";
import { client } from "../../client/kaleidoClient";

interface UseThreadContext {
  (props?: {}): {
    isBusy: boolean;
    rerank: boolean;
    setRerank: (rerank: boolean) => void;
    getRecommendations: typeof client.getRecommendations;
    postToThread: typeof client.postToThread;
    createThread: typeof client.createThread;
  };
}

export const useThreadContext: UseThreadContext = () => {
  const { isBusy, setBusy, rerank, setRerank } = useContext(ThreadContext) as ThreadContextProps;

  const getRecommendations = async (uid: number, tid: number): Promise<Product[]> => {
    setBusy(true);

    try {
      const response = await client.getRecommendations(uid, tid, rerank);
      setBusy(false);
      return response;
    } catch (error) {
      // TODO: Display that search needs refinement
      setBusy(false);
      return [];
    }
  };

  const postToThread = async (uid: number, tid: number, content: { query?: string, answers?: UserAnswer[] }): Promise<QueryEvaluation> => {
    setBusy(true);
    const response = await client.postToThread(uid, tid, content);
    setBusy(false);
    return response;
  };

  const createThread = async (uid: number, query?: string): Promise<QueryEvaluation> => {
    setBusy(true);
    const response = await client.createThread(uid, query);
    setBusy(false);
    return response;
  };

  return { isBusy, rerank, setRerank, getRecommendations, postToThread, createThread };
};
