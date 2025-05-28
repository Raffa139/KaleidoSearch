import * as Http from "./clientBase";
import type { ProductSummary } from "./types";

export class ProductsClient extends Http.ClientBase {
  resource(): string {
    return "products";
  }

  summarize(ids: number[], length: number = 25): Promise<ProductSummary[]> {
    return Http.post(`${this.baseUrl()}/summarize?length=${length}`, ids);
  }
}
