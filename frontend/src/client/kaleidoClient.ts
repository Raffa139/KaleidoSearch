import type { Answer, Product, QueryEvaluation, User } from "./types";

const DEFAULT_HEADERS = {
  "Content-Type": "application/json"
};



class KaleidoClient {
  url: string;

  constructor(host: string, port: number) {
    this.url = `http://${host}:${port}`;
  }

  async createUser(sub_id: string, username: string, picture_url: string | null): Promise<User> {
    const response = await fetch(`${this.url}/users`, {
      method: "POST",
      headers: DEFAULT_HEADERS,
      body: JSON.stringify({ sub_id, username, picture_url })
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to create user");
    }

    return response.json();
  }

  async getUserById(uid: number): Promise<User> {
    const response = await fetch(`${this.url}/users/${uid}`, { headers: DEFAULT_HEADERS });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch user");
    }

    return response.json();
  }

  async getUserThreads(uid: number): Promise<Array<{ thread_id: number }>> {
    const response = await fetch(`${this.url}/users/${uid}/threads`, {
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch user threads");
    }

    return response.json();
  }

  async createThread(uid: number): Promise<{ thread_id: number }> {
    const response = await fetch(`${this.url}/users/${uid}/threads`, {
      method: "POST",
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to create new thread");
    }

    return response.json();
  }

  async getUserThread(uid: number, tid: number): Promise<QueryEvaluation> {
    const response = await fetch(`${this.url}/users/${uid}/threads/${tid}`, {
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch thread");
    }

    return response.json();
  }

  async postToThread(uid: number, tid: number, content: { query?: string, answers?: Answer[] }): Promise<QueryEvaluation> {
    if (!content.query && !content.answers) {
      throw new Error("Either query string or answers must be provided");
    }

    // TODO: Already anwsered questions can be remove by an empty string, add flag to Answer type
    const payload = {
      query: content.query?.trim() || undefined,
      answers: content.answers?.map(a => ({ ...a, answer: a.answer.trim() })).filter(a => a.answer)
    };

    console.log("Payload:", payload);

    const response = await fetch(`${this.url}/users/${uid}/threads/${tid}`, {
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

  async getRecommendations(uid: number, tid: number): Promise<Product[]> {
    const response = await fetch(`${this.url}/users/${uid}/threads/${tid}/recommendations`, {
      headers: DEFAULT_HEADERS
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch product recommendations");
    }

    return response.json();
  }
}

export const client = new KaleidoClient("localhost", 8000);
