import { BookmarksClient } from "./bookmarksClient";
import * as Http from "./clientBase";
import { ThreadsClient } from "./threadsClient";
import type { User } from "./types";

export class UsersClient extends Http.ClientBase {
  Bookmarks: BookmarksClient;
  Threads: ThreadsClient;

  constructor(host: string, port: number, rootPath: string = "") {
    super(host, port, rootPath);
    this.Bookmarks = new BookmarksClient(host, port, `${rootPath}/${this.resource()}`);
    this.Threads = new ThreadsClient(host, port, `${rootPath}/${this.resource()}`);
  }

  resource(): string {
    return "users";
  }

  create(sub_id: string, username: string, picture_url: string | null): Promise<User> {
    return Http.post(`${this.baseUrl()}`, { sub_id, username, picture_url });
  }

  getAuthenticated(): Promise<User> {
    return Http.get(`${this.baseUrl()}/me`);
  }
}
