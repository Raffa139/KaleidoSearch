import { BookmarksClient } from "./bookmarksClient";
import * as Http from "./clientBase";
import { ThreadsClient } from "./threadsClient";
import type { User } from "./types";

export class UsersClient extends Http.ClientBase {
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

  create(sub_id: string, username: string, picture_url: string | null): Promise<User> {
    return Http.post(`${this.baseUrl()}`, { sub_id, username, picture_url });
  }

  getById(uid: number | string): Promise<User> {
    return Http.get(`${this.baseUrl()}/${uid}`);
  }
}
