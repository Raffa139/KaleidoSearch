import { BookmarksClient } from "./bookmarksClient";
import { BaseClient } from "./baseClient";
import { ThreadsClient } from "./threadsClient";
import type { User } from "./types";

export class UsersClient extends BaseClient {
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
    return this.Http.post({ sub_id, username, picture_url });
  }

  getAuthenticated(): Promise<User> {
    return this.Http.get("me");
  }
}
