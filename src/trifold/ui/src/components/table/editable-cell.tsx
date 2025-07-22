import type React from "react"

import { useState, useEffect } from "react"
import type { Row, Column, Table } from "@tanstack/react-table"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"
import type { DessertOut } from "@/lib/api"

interface EditableCellProps {
  getValue: () => any
  row: Row<DessertOut>
  column: Column<DessertOut>
  table: Table<DessertOut>
  type?: "text" | "number" | "textarea"
  format?: (value: any) => string
  className?: string
}

export function EditableCell({ getValue, row, column, table, type = "text", format, className }: EditableCellProps) {
  const initialValue = getValue()
  const [value, setValue] = useState(initialValue)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  const onBlur = () => {
    setIsEditing(false)
    const updateData = (table.options.meta as any)?.updateData
    if (updateData) {
      updateData(row.index, column.id, value)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && type !== "textarea") {
      onBlur()
    }
    if (e.key === "Escape") {
      setValue(initialValue)
      setIsEditing(false)
    }
  }

  if (isEditing) {
    if (type === "textarea") {
      return (
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={onBlur}
          onKeyDown={onKeyDown}
          className={cn("min-h-[60px] resize-none", className)}
          autoFocus
        />
      )
    }

    return (
      <Input
        value={value}
        onChange={(e) => setValue(type === "number" ? Number(e.target.value) : e.target.value)}
        onBlur={onBlur}
        onKeyDown={onKeyDown}
        type={type}
        className={cn("h-8", className)}
        autoFocus
      />
    )
  }

  const displayValue = format ? format(value) : value

  return (
    <div
      onClick={() => setIsEditing(true)}
      className={cn(
        "cursor-pointer rounded px-2 py-1 hover:bg-muted/50 transition-colors min-h-[32px] flex items-center",
        type === "textarea" && "min-h-[60px] items-start py-2",
        className,
      )}
      title="Click to edit"
    >
      {type === "textarea" ? (
        <span className="whitespace-pre-wrap break-words">{displayValue}</span>
      ) : (
        <span className="truncate">{displayValue}</span>
      )}
    </div>
  )
}
