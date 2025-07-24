import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Trash2 } from "lucide-react";
import { useDeleteDessert, type DessertOut } from "@/lib/api";
import { refetchDesserts } from "@/lib/utils";

interface DeleteDessertModalProps {
  dessert: DessertOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DeleteDessertModal({
  dessert,
  open,
  onOpenChange,
}: DeleteDessertModalProps) {
  const mutation = useDeleteDessert();

  const handleDelete = async () => {
    try {
      await mutation.mutateAsync({ dessertId: dessert.id });
      onOpenChange(false);
      refetchDesserts();
    } catch (error) {
      // Error is handled by the store, but we could show a toast here
      console.error("Failed to delete dessert:", error);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Delete Dessert</SheetTitle>
          <SheetDescription>
            Are you sure you want to delete "{dessert.name}"? This action cannot
            be undone.
          </SheetDescription>
        </SheetHeader>

        <div className="py-6">
          <div className="rounded-lg border p-4 bg-muted">
            <h4 className="font-medium">{dessert.name}</h4>
            <p className="text-sm text-muted-foreground mt-1">
              {dessert.description}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Price: ${dessert.price} • Stock: {dessert.leftInStock}
            </p>
          </div>
        </div>

        <SheetFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={mutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleDelete}
            disabled={mutation.isPending}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            {mutation.isPending ? "Deleting..." : "Delete Dessert"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
