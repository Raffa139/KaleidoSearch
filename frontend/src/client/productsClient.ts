import { BaseClient } from "./baseClient";
import type { Product, ProductSummary } from "./types";

export class ProductsClient extends BaseClient {
  resource(): string {
    return "products";
  }

  getAll(ids?: number[]): Promise<Product[]> {
    const idsParam = ids?.join(",");
    return this.Http.get(`${idsParam ? "?ids=" + idsParam : ""}`);
  }

  async summarize(ids: number[], length: number = 25): Promise<ProductSummary[]> {
    if (ids.length > 0) {
      return this.Http.post(ids, `summarize?length=${length}`);
    }

    return [];
  }
}
