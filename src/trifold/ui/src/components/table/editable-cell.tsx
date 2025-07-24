import type React from "react";

import { useState } from "react";
import type { Row, Column, Table } from "@tanstack/react-table";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn, refetchDesserts } from "@/lib/utils";
import { type DessertOut, useUpdateDessert } from "@/lib/api";

interface EditableCellProps {
  getValue: () => any;
  row: Row<DessertOut>;
  column: Column<DessertOut>;
  table: Table<DessertOut>;
  type?: "text" | "number" | "textarea";
  format?: (value: any) => string;
  className?: string;
}

export function EditableCell({
  getValue,
  row,
  column,
  type = "text",
  format,
  className,
}: EditableCellProps) {
  const initialValue = getValue();
  const [value, setValue] = useState(initialValue);
  const [isEditing, setIsEditing] = useState(false);
  const mutation = useUpdateDessert();

  const onBlur = async () => {
    setIsEditing(false);
    if (value !== initialValue) {
      try {
        let newRow = row.original;
        let key = column.id as keyof DessertOut;
        // @ts-expect-error: We are updating a known property dynamically
        newRow[key] = value;

        await mutation.mutateAsync(
          {
            dessertId: row.original.id,
            data: newRow,
          },
          {
            onSuccess: () => {
              refetchDesserts();
            },
          },
        );
      } catch (error) {
        // Revert value on error
        setValue(initialValue);
        console.error("Failed to update dessert field:", error);
      }
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && type !== "textarea") {
      onBlur();
    }
    if (e.key === "Escape") {
      setValue(initialValue);
      setIsEditing(false);
    }
  };

  const onChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    let newValue: any = e.target.value;
    if (type === "number") {
      newValue = parseFloat(newValue) || 0;
    }
    setValue(newValue);
  };

  const displayValue = format ? format(value) : value;

  if (isEditing) {
    if (type === "textarea") {
      return (
        <Textarea
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          onKeyDown={onKeyDown}
          className={cn("min-h-[60px] resize-none", className)}
          autoFocus
        />
      );
    }

    return (
      <Input
        type={type === "number" ? "number" : "text"}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        onKeyDown={onKeyDown}
        className={cn("h-8", className)}
        autoFocus
      />
    );
  }

  return (
    <div
      onClick={() => setIsEditing(true)}
      className={cn(
        type === "textarea" ? "min-h-[60px] whitespace-pre-wrap py-2" : "h-8",
        "flex w-full cursor-pointer items-start rounded-md border border-transparent px-3 text-sm hover:border-input hover:bg-accent",
        className,
      )}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          setIsEditing(true);
        }
      }}
    >
      {displayValue}
    </div>
  );
}
