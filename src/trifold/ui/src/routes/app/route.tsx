import Layout from "@/components/Layout";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/app")({
  component: RouteComponent,
});

function RouteComponent() {
  return <Layout />;
}
