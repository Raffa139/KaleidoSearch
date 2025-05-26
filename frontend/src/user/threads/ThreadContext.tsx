import { createContext, useState, type FunctionComponent, type ReactNode } from "react";

export interface ThreadContextProps {
  isBusy: boolean;
  rerank: boolean;
  setBusy: (busy: boolean) => void;
  setRerank: (rerank: boolean) => void;
}

interface ThreadContextWrapperProps {
  children: ReactNode;
}

export const ThreadContext = createContext<Partial<ThreadContextProps>>({});

export const ThreadContextWrapper: FunctionComponent<ThreadContextWrapperProps> = ({ children }) => {
  const [isBusy, setBusy] = useState<boolean>(false);
  const [rerank, setRerank] = useState<boolean>(false);

  return (
    <ThreadContext.Provider value={{ isBusy, setBusy, rerank, setRerank }}>
      {children}
    </ThreadContext.Provider>
  );
};
