import { createContext, useState, type FunctionComponent } from "react";
import { Thread } from "./Thread";

export interface ThreadContextProps {
  isBusy: boolean;
  rerank: boolean;
  setBusy: (busy: boolean) => void;
  setRerank: (rerank: boolean) => void;
}

export const ThreadContext = createContext<Partial<ThreadContextProps>>({});

export const ThreadWithContext: FunctionComponent = () => {
  const [isBusy, setBusy] = useState<boolean>(false);
  const [rerank, setRerank] = useState<boolean>(false);

  return (
    <ThreadContext.Provider value={{ isBusy, setBusy, rerank, setRerank }}>
      <Thread />
    </ThreadContext.Provider>
  );
};
