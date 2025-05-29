import { Fragment, useEffect, useState, type FunctionComponent } from "react";
import type { Product, ProductSummary } from "../client/types";
import { client } from "../client/kaleidoClient";
import { ProductCard, type AdditionalProductCardProps } from "./ProductCard";

const CACHED_SUMMARIES: ProductSummary[] = [];

interface ProductProviderProps extends AdditionalProductCardProps {
  products: Product[];
}

export const ProductProvider: FunctionComponent<ProductProviderProps> = ({ products, ...additional }) => {
  const [summarizedProducts, setSummarizedProducts] = useState<Array<Product & Partial<ProductSummary>>>(products);

  useEffect(() => {
    const fetchProductSummaries = async () => {
      const productIds = products.map(product => product.id);
      const notInCache = productIds.filter(id => !CACHED_SUMMARIES.some(summary => summary.id === id));

      if (notInCache.length > 0) {
        const newSummaries = await client.Products.summarize(notInCache);
        CACHED_SUMMARIES.push(...newSummaries);
      }

      const summarized = products.map(product => ({
        ...product,
        ...CACHED_SUMMARIES.find(summary => summary.id === product.id)
      }))

      setSummarizedProducts(summarized);
    };

    if (products.length > 0) {
      fetchProductSummaries();
    }
  }, [products]);

  return products.length > 0 ? summarizedProducts.map(summarizedProduct => (
    <Fragment key={summarizedProduct.id}>
      <ProductCard {...summarizedProduct} {...additional} />
    </Fragment>
  )) : null;
};
