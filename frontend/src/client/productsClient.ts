import * as Http from "./clientBase";
import type { Product, ProductSummary } from "./types";

export class ProductsClient extends Http.ClientBase {
  resource(): string {
    return "products";
  }

  getAll(ids?: number[]): Promise<Product[]> {
    const idsParam = ids?.join(",");
    return Http.get(`${this.baseUrl()}${idsParam ? "/?ids=" + idsParam : ""}`);
  }

  async summarize(ids: number[], length: number = 25): Promise<ProductSummary[]> {
    if (ids.length > 0) {
      return Http.post(`${this.baseUrl()}/summarize?length=${length}`, ids);
    }

    return [];
  }
}
