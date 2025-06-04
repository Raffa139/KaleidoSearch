import { BaseClient } from "./baseClient";
import type { AnsweredQuestion, FollowUpQuestion, HasId, Product, QueryEvaluation, Thread, UserAnswer } from "./types";

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

  async create(query?: string): Promise<QueryEvaluation> {
    return this.filterUniqueQuestions(await this.Http.post(query ? { query: query.trim() } : undefined));
  }

  async getQueryEvaluation(tid: number | string): Promise<QueryEvaluation> {
    return this.filterUniqueQuestions(await this.Http.get(`${tid}`));
  }

  async post(tid: number | string, content: { query?: string, answers?: UserAnswer[] }): Promise<QueryEvaluation> {
    if (!content.query && !content.answers) {
      throw new Error("Either query string or answers must be provided");
    }

    const payload = {
      query: content.query?.trim() || undefined,
      answers: content.answers
        ?.map(a => ({ ...a, answer: a.answer.trim() }))
        .filter(a => a.remove || a.answer)
    };

    return this.filterUniqueQuestions(await this.Http.post(payload, `${tid}`));
  }

  delete(tid: number | string): Promise<void> {
    return this.Http.delete_(`${tid}`);
  }

  getRecommendations(tid: number | string, rerank: boolean = false): Promise<Product[]> {
    return this.Http.get(`${tid}`, `recommendations?rerank=${rerank}`);
  }

  private filterUniqueQuestions(queryEvaluation: QueryEvaluation): QueryEvaluation {
    const [filteredFollowUpQuestions, filteredAnsweredQuestions] = this.acrossAllUniqueById(
      queryEvaluation.follow_up_questions,
      queryEvaluation.answered_questions
    ) as [FollowUpQuestion[], AnsweredQuestion[]];

    return {
      ...queryEvaluation,
      follow_up_questions: filteredFollowUpQuestions,
      answered_questions: filteredAnsweredQuestions
    }
  }

  private acrossAllUniqueById<T extends HasId>(...lists: T[][]): T[][] {
    const filtered: T[][] = [];
    const seen = new Set();
    lists.forEach(list => filtered.push(list.filter(({ id }) => seen.has(id) ? false : seen.add(id))));
    return filtered;
  }
}
