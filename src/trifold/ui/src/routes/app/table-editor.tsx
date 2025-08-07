import { createFileRoute } from "@tanstack/react-router";
import { AddDessertModal } from "@/components/table/add-dessert-modal";
import DataTable from "@/components/table/data-table";

export const Route = createFileRoute("/app/table-editor")({
  component: TableEditor,
});

function TableEditor() {
  return (
    <div className="container mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dessert Menu</h1>
          <p className="text-muted-foreground">Manage your dessert inventory</p>
        </div>
        <AddDessertModal />
      </div>
      <DataTable />
    </div>
  );
}
