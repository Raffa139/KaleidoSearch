import { Fragment, useState, type FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import { ProductCard } from "../../products/ProductCard";
import { SearchBar } from "./search/SearchBar";
import { client } from "../../client/kaleidoClient";
import type { Product, QueryEvaluation, User } from "../../client/types";
import "./thread.css";

export const Thread: FunctionComponent = () => {
  const thread = useLoaderData<QueryEvaluation>();
  const user = useOutletContext<User>();

  const [queryEvaluation, setQueryEvaluation] = useState<QueryEvaluation | undefined>(thread);
  const [products, setProducts] = useState<Product[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [hasSearchResults, setHasSearchResults] = useState<boolean>(false);

  console.log("Logged in as", user, "in thread", thread);

  const handleSearch = async (queryEvaluation?: QueryEvaluation) => {
    setQueryEvaluation(queryEvaluation);
    const products = await client.getRecommendations(user.id, thread.thread_id);
    setProducts(products);
    setHasSearched(true);
    setHasSearchResults(products.length > 0);
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

        {hasSearched && !hasSearchResults && (
          <p>No results found. Please try a different search.</p>
        )}
      </div>
    </div>
  );
};