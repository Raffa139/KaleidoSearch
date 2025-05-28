import { ClientBase, DEFAULT_HEADERS } from "./clientBase";
import type { Product, QueryEvaluation, Thread, UserAnswer } from "./types";

export class ThreadsClient extends ClientBase {
  uid: number | string;

  constructor(host: string, port: number, uid: number | string, rootPath: string = "") {
    super(host, port, rootPath);
    this.uid = uid;
  }

  resource(): string {
    return "threads";
  }

  baseUrl(): string {
    return super.baseUrl().replace("{uid}", String(this.uid));
  }

  async getAll(): Promise<Thread[]> {
    const response = await fetch(`${this.baseUrl()}`, {
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch user threads");
    }

    const json = await response.json();

    // Map dates from UTC to browsers timezone
    return json.map((thread: Thread) => ({
      ...thread,
      created_at: new Date(`${thread.created_at}Z`),
      updated_at: new Date(`${thread.updated_at}Z`)
    }));
  }

  async create(query?: string): Promise<QueryEvaluation> {
    const response = await fetch(`${this.baseUrl()}`, {
      method: "POST",
      headers: DEFAULT_HEADERS,
      body: query ? JSON.stringify({ query: query.trim() }) : undefined
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to create new thread");
    }

    return response.json();
  }

  async getQueryEvaluation(tid: number | string): Promise<QueryEvaluation> {
    const response = await fetch(`${this.baseUrl()}/${tid}`, {
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch thread");
    }

    return response.json();
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

    console.log("Payload:", payload);

    const response = await fetch(`${this.baseUrl()}/${tid}`, {
      method: "POST",
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to post to thread");
    }

    return response.json();
  }

  async delete(tid: number | string): Promise<void> {
    const response = await fetch(`${this.baseUrl()}/${tid}`, {
      method: "DELETE",
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to delete thread");
    }
  }

  async getRecommendations(tid: number | string, rerank: boolean = false): Promise<Product[]> {
    const response = await fetch(`${this.baseUrl()}/${tid}/recommendations?rerank=${rerank}`, {
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch product recommendations");
    }

    return response.json();
  }
}
