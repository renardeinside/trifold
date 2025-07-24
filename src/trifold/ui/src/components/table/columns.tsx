"use client";

import { type ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, MoreHorizontal, Trash2, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { EditableCell } from "./editable-cell";
import { DeleteDessertModal } from "./delete-dessert-modal";
import type { DessertOut } from "@/lib/api";
import { useState } from "react";
import { toast } from "sonner";

export const columns: ColumnDef<DessertOut>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ getValue, row, column, table }) => {
      return (
        <EditableCell
          getValue={getValue}
          row={row}
          column={column}
          table={table}
          type="text"
          className="font-medium"
        />
      );
    },
  },
  {
    accessorKey: "price",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Price
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ getValue, row, column, table }) => {
      return (
        <EditableCell
          getValue={getValue}
          row={row}
          column={column}
          table={table}
          type="number"
          format={(value) => `$${Number(value).toFixed(2)}`}
          className="font-mono"
        />
      );
    },
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ getValue, row, column, table }) => {
      return (
        <EditableCell
          getValue={getValue}
          row={row}
          column={column}
          table={table}
          type="textarea"
          className="min-w-96 w-full max-w-md whitespace-normal break-words text-sm text-muted-foreground"
        />
      );
    },
  },
  {
    accessorKey: "leftInStock",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Stock
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ getValue, row, column, table }) => {
      return (
        <EditableCell
          getValue={getValue}
          row={row}
          column={column}
          table={table}
          type="number"
          className="font-mono w-16"
        />
      );
    },
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const dessert = row.original;

      // Local state to control delete modal visibility
      const [open, setOpen] = useState(false);

      const copyId = async () => {
        try {
          await navigator.clipboard.writeText(dessert.id.toString());
          toast.success("ID copied to clipboard");
        } catch (err) {
          toast.error("Failed to copy ID to clipboard");
        }
      };

      return (
        <>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onSelect={copyId}>
                <Copy className="mr-2 h-4 w-4" /> Copy ID
              </DropdownMenuItem>
              <DropdownMenuItem
                onSelect={(e) => {
                  e.preventDefault();
                  setOpen(true);
                }}
              >
                <Trash2 className="mr-2 h-4 w-4 text-red-600" /> Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Delete confirmation modal */}
          <DeleteDessertModal
            dessert={dessert}
            open={open}
            onOpenChange={setOpen}
          />
        </>
      );
    },
  },
];
