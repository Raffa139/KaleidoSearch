import { Fragment, useEffect, useState, type FunctionComponent } from "react";
import type { Product, ProductSummary } from "../client/types";
import { client } from "../client/kaleidoClient";
import { ProductCard } from "./ProductCard";

const CACHED_SUMMARIES: ProductSummary[] = [];

interface ProductProviderProps {
  products: Product[];
}

export const ProductProvider: FunctionComponent<ProductProviderProps> = ({ products }) => {
  const [productSummaries, setProductSummaries] = useState<ProductSummary[]>([]);

  useEffect(() => {
    const fetchProductSummaries = async () => {
      const productIds = products.map(p => p.id);
      const notInCache = productIds.filter(id => !CACHED_SUMMARIES.some(summary => summary.id === id));

      if (notInCache.length > 0) {
        const newSummaries = await client.Products.summarize(notInCache);
        CACHED_SUMMARIES.push(...newSummaries);
      }

      const summaries = CACHED_SUMMARIES.filter(summary => productIds.includes(summary.id));
      setProductSummaries(summaries);
    };

    if (products.length > 0) {
      fetchProductSummaries();
    }
  }, [products]);

  return products ? products.map((product, i) => (
    <Fragment key={product.id}>
      <ProductCard {...product} {...productSummaries[i]} />
    </Fragment>
  )) : null;
};
