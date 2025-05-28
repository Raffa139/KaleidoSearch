import { useEffect, useState, type FunctionComponent } from "react";
import type { Product } from "../client/types";
import { client } from "../client/kaleidoClient";
import { ProductProvider } from "./ProductProvider";

interface ProductProviderByIdsProps {
  productIds: number[];
}

export const ProductProviderByIds: FunctionComponent<ProductProviderByIdsProps> = ({ productIds }) => {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    const fetchProducts = async () => {
      const products = await client.Products.getAll(productIds);
      setProducts(products);
    };

    if (productIds.length > 0) {
      fetchProducts();
    }
  }, [productIds]);

  return products ? <ProductProvider products={products} /> : null;
};
