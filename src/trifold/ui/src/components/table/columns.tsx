import type { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown, Package, Euro, Copy, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { DessertOut } from "@/lib/api"
import { EditableCell } from "@/components/table/editable-cell"

export const columns: ColumnDef<DessertOut>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="h-8 px-2 lg:px-3"
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ getValue, row, column, table }) => (
      <EditableCell getValue={getValue} row={row} column={column} table={table} type="text" className="font-medium" />
    ),
  },
  {
    accessorKey: "price",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="h-8 px-2 lg:px-3"
        >
          <Euro className="mr-2 h-4 w-4" />
          Price
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ getValue, row, column, table }) => (
      <EditableCell
        getValue={getValue}
        row={row}
        column={column}
        table={table}
        type="number"
        format={(value) => `€${Number(value).toFixed(2)}`}
        className="font-mono"
      />
    ),
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ getValue, row, column, table }) => (
      <EditableCell
        getValue={getValue}
        row={row}
        column={column}
        table={table}
        type="textarea"
        className="max-w-[300px] text-sm text-muted-foreground"
      />
    ),
  },
  {
    accessorKey: "leftInStock",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="h-8 px-2 lg:px-3"
        >
          <Package className="mr-2 h-4 w-4" />
          Stock
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
    cell: ({ getValue, row, column, table }) => {
      const stock = getValue<number>()
      return (
        <div className="flex items-center gap-2">
          <EditableCell
            getValue={getValue}
            row={row}
            column={column}
            table={table}
            type="number"
            className="font-mono w-16"
          />
          <Badge variant={stock === 0 ? "destructive" : stock < 10 ? "secondary" : "default"} className="text-xs">
            {stock === 0 ? "Out" : stock < 10 ? "Low" : "In Stock"}
          </Badge>
        </div>
      )
    },
  },
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const id = row.original.id

      const handleCopyId = () => {
        navigator.clipboard.writeText(id.toString())
        // You could add a toast notification here
      }

      const handleDeleteRow = () => {
        // This is just for UI demonstration - no actual deletion logic
        console.log(`Delete row with ID: ${id}`)
        // You could add actual deletion logic here
      }

      return (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopyId}
            className="h-8 w-8 p-0"
            title="Copy ID"
          >
            <Copy className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDeleteRow}
            className="h-8 w-8 p-0 text-destructive hover:text-destructive"
            title="Delete row"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )
    },
  },
]
