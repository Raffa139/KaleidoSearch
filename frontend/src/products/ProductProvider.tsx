import { Fragment, useEffect, useState, type FunctionComponent } from "react";
import type { Product, ProductSummary } from "../client/types";
import { client } from "../client/kaleidoClient";
import { ProductCard } from "./ProductCard";

interface ProductProviderProps {
  products: Product[];
}

export const ProductProvider: FunctionComponent<ProductProviderProps> = ({ products }) => {
  const [productSummaries, setProductSummaries] = useState<Partial<ProductSummary>[]>([]);

  useEffect(() => {
    const fetchProductSummary = async () => {
      try {
        const summaries = await client.Products.summarize(products.map(p => p.id));
        setProductSummaries(summaries);
      } catch (error) {
        setProductSummaries(products.map(p => ({
          ai_title: p.title,
          ai_description: p.description
        })));
      }
    };

    if (products.length > 0) {
      fetchProductSummary();
    }
  }, [products]);

  return products ? products.map((product, i) => (
    <Fragment key={product.id}>
      <ProductCard {...product} {...productSummaries[i]} />
    </Fragment>
  )) : null;
};
