import { BaseClient } from "./baseClient";
import type { Product, QueryEvaluation, Thread, UserAnswer } from "./types";

export class ThreadsClient extends BaseClient {
  resource(): string {
    return "me/threads";
  }

  async getAll(): Promise<Thread[]> {
    const threads: Thread[] = await this.Http.get();

    // Map dates from UTC to browsers timezone
    return threads.map((thread: Thread) => ({
      ...thread,
      created_at: new Date(`${thread.created_at}Z`),
      updated_at: new Date(`${thread.updated_at}Z`)
    }));
  }

  create(query?: string): Promise<QueryEvaluation> {
    return this.Http.post(query ? { query: query.trim() } : undefined);
  }

  getQueryEvaluation(tid: number | string): Promise<QueryEvaluation> {
    return this.Http.get(`${tid}`);
  }

  post(tid: number | string, content: { query?: string, answers?: UserAnswer[] }): Promise<QueryEvaluation> {
    if (!content.query && !content.answers) {
      throw new Error("Either query string or answers must be provided");
    }

    const payload = {
      query: content.query?.trim() || undefined,
      answers: content.answers
        ?.map(a => ({ ...a, answer: a.answer.trim() }))
        .filter(a => a.remove || a.answer)
    };

    console.log("Payload:", payload);

    return this.Http.post(payload, `${tid}`);
  }

  delete(tid: number | string): Promise<void> {
    return this.Http.delete_(`${tid}`);
  }

  getRecommendations(tid: number | string, rerank: boolean = false): Promise<Product[]> {
    return this.Http.get(`${tid}`, `recommendations?rerank=${rerank}`);
  }
}
