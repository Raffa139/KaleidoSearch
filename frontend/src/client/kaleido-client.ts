const DEFAULT_HEADERS = {
  "Content-Type": "application/json"
};

export interface User {
  id: number;
  sub_id: string;
  username: string | null;
  picture_url: string | null;
}

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
}

export const client = new KaleidoClient("localhost", 8000);
