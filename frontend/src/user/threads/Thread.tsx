import { Fragment, useState, type FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import type { UserLoaderData } from "../../authentication/userLoader";
import { ProductCard } from "../../products/ProductCard";
import { SearchBar } from "./search/SearchBar";
import { client } from "../../client/kaleidoClient";
import type { Product, QueryEvaluation } from "../../client/types";
import "./thread.css";

export const Thread: FunctionComponent = () => {
  const [queryEvaluation, setQueryEvaluation] = useState<QueryEvaluation>();
  const [products, setProducts] = useState<Product[]>([]);

  const { thread_id } = useLoaderData();
  const { user } = useOutletContext<UserLoaderData>();

  console.log("Logged in as", user, "in thread", thread_id);

  const handleSearch = async (queryEvaluation?: QueryEvaluation) => {
    setQueryEvaluation(queryEvaluation);
    const products = await client.getRecommendations(user.id, thread_id);
    console.log("Products:", products);
    setProducts(products);
  };

  return (
    <div className="container">
      <SearchBar queryEvaluation={queryEvaluation} onSearch={handleSearch} />

      <div className="results-container">
        {products.map((product) => (
          <Fragment key={product.url}>
            <ProductCard {...product} />
          </Fragment>
        ))}
      </div>
    </div>
  );
};