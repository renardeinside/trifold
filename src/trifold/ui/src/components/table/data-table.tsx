import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable,
  getFilteredRowModel,
  type ColumnFiltersState,
} from "@tanstack/react-table";
import { Suspense, useEffect, useState } from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDessertsSuspense, type DessertOut } from "@/lib/api";
import { columns } from "@/components/table/columns";
import { Skeleton } from "@/components/ui/skeleton";
import FadeIn from "@/components/FadeIn";

enum OperationType {
  INSERT = "INSERT",
  UPDATE = "UPDATE",
  DELETE = "DELETE",
}

interface Notification {
  operation: OperationType;
  data: DessertOut;
}

function DessertTableContent({ initialData }: { initialData: DessertOut[] }) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: "id", desc: false },
  ]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [data, setData] = useState<DessertOut[]>(initialData);

  useEffect(() => {
    const eventSource = new EventSource("/api/desserts/events");
    eventSource.onmessage = (event) => {
      // unpack the event data
      const { operation, data } = JSON.parse(event.data) as Notification;
      switch (operation) {
        case OperationType.INSERT:
          setData((prev) => [...prev, data]);
          break;
        case OperationType.UPDATE:
          setData((prev) => prev.map((d) => (d.id === data.id ? data : d)));
          break;
        case OperationType.DELETE:
          setData((prev) => prev.filter((d) => d.id !== data.id));
          break;
      }
    };

    // Cleanup function to close the EventSource
    return () => {
      eventSource.close();
    };
  }, []);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
  });

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} className="font-semibold">
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="hover:bg-muted/50"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="p-0">
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-between space-x-2 py-4">
        <div className="text-sm text-muted-foreground">
          Showing {table.getFilteredRowModel().rows.length} dessert(s)
        </div>
      </div>
    </>
  );
}

function TableSkeleton() {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((_, i) => (
              <TableHead key={i}>
                <Skeleton className="h-6 w-full" />
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              {columns.map((_, j) => (
                <TableCell key={j} className="p-4">
                  <Skeleton className="h-6 w-full" />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function DataTableLoader() {
  const { data } = useDessertsSuspense({
    query: {
      refetchOnWindowFocus: true,
      refetchOnMount: true,
      select: (d) => d.data,
    },
  });

  return (
    <FadeIn>
      <DessertTableContent initialData={data ?? []} />
    </FadeIn>
  );
}

function DataTable() {
  return (
    <Suspense fallback={<TableSkeleton />}>
      <DataTableLoader />
    </Suspense>
  );
}

export default DataTable;
