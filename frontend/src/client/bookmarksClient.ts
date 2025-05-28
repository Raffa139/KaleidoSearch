import * as Http from "./clientBase";
import type { Bookmark } from "./types";

export class BookmarksClient extends Http.ClientBase {
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

  async getAll(): Promise<Bookmark[]> {
    const bookmarks: Bookmark[] = await Http.get(`${this.baseUrl()}`);

    // Map date from UTC to browsers timezone
    return bookmarks.map((bookmark) => ({
      ...bookmark,
      created_at: new Date(`${bookmark.created_at}Z`)
    }));
  }

  async getByProductId(product_id: number): Promise<Bookmark | null> {
    try {
      return await Http.get(`${this.baseUrl()}/${product_id}`);
    } catch (error) {
      return null;
    }
  }

  create(product_id: number): Promise<Bookmark> {
    return Http.post(`${this.baseUrl()}`, { product_id });
  }

  delete(id: number | string): Promise<void> {
    return Http.delete_(`${this.baseUrl()}/${id}`)
  }
}
