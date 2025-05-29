import { useEffect, useState, type FunctionComponent } from "react";
import type { Product } from "../client/types";
import { client } from "../client/kaleidoClient";
import { ProductProvider } from "./ProductProvider";
import type { AdditionalProductCardProps } from "./ProductCard";

interface ProductProviderByIdsProps extends AdditionalProductCardProps {
  productIds: number[];
}

export const ProductProviderByIds: FunctionComponent<ProductProviderByIdsProps> = ({ productIds, ...additional }) => {
  const [products, setProducts] = useState<Product[]>([]);

  const handleBookmarkRemove = (productId: number) => {
    setProducts(prevProducts => prevProducts.filter(product => product.id !== productId));
  };

  useEffect(() => {
    const fetchProducts = async () => {
      const products = await client.Products.getAll(productIds);
      setProducts(products);
    };

    if (productIds.length > 0) {
      fetchProducts();
    }
  }, [productIds]);

  return products.length > 0 ? (
    <ProductProvider onBookmarkRemove={handleBookmarkRemove} products={products} {...additional} />
  ) : null;
};
