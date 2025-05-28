import { BookmarksClient } from "./bookmarksClient";
import { ClientBase, DEFAULT_HEADERS } from "./clientBase";
import { ThreadsClient } from "./threadsClient";
import type { User } from "./types";

export class UsersClient extends ClientBase {
  Bookmarks: (uid: number | string) => BookmarksClient;
  Threads: (uid: number | string) => ThreadsClient;

  constructor(host: string, port: number, rootPath: string = "") {
    super(host, port, rootPath);
    this.Bookmarks = (uid: number | string) => new BookmarksClient(host, port, uid, `${rootPath}/${this.resource()}/{uid}`);
    this.Threads = (uid: number | string) => new ThreadsClient(host, port, uid, `${rootPath}/${this.resource()}/{uid}`);
  }

  resource(): string {
    return "users";
  }

  async create(sub_id: string, username: string, picture_url: string | null): Promise<User> {
    const response = await fetch(`${this.baseUrl()}`, {
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

  async getById(uid: number | string): Promise<User> {
    const response = await fetch(`${this.baseUrl()}/${uid}`, { headers: DEFAULT_HEADERS });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch user");
    }

    return response.json();
  }
}