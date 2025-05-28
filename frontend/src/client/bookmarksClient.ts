import { ClientBase } from "./clientBase";

export class BookmarksClient extends ClientBase {
  uid: number | string;

  constructor(host: string, port: number, uid: number | string, rootPath: string = "") {
    super(host, port, rootPath);
    this.uid = uid;
  }

  resource(): string {
    return "bookmarks";
  }

  baseUrl(): string {
    return super.baseUrl().replace("{uid}", String(this.uid));
  }
}
