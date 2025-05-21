import type { Answer, QueryEvaluation, User } from "./types";

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
      throw new Error("Failed to create user");
    }

    return response.json();
  }

  async getUserById(uid: number): Promise<User> {
    const response = await fetch(`${this.url}/users/${uid}`, { headers: DEFAULT_HEADERS });

    if (!response.ok) {
      throw new Error("Failed to fetch user");
    }

    return response.json();
  }

  async startNewTread(uid: number, query: string): Promise<QueryEvaluation> {
    const response = await fetch(`${this.url}/users/${uid}/threads`, {
      method: "POST",
      headers: DEFAULT_HEADERS,
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      throw new Error("Failed to create user");
    }

    return response.json();
  }

  async postToThread(uid: number, tid: number, query?: string, answers?: Answer[]): Promise<QueryEvaluation> {
    if (!query && !answers) {
      throw new Error("Either query or answers must be provided");
    }

    const response = await fetch(`${this.url}/users/${uid}/threads/${tid}`, {
      method: "POST",
      headers: DEFAULT_HEADERS,
      body: JSON.stringify({ query, answers })
    });

    if (!response.ok) {
      throw new Error("Failed to create user");
    }

    return response.json();
  }
}

export const client = new KaleidoClient("localhost", 8000);
