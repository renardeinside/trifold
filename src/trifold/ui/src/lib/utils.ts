import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { useDesserts } from "./api";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export async function refetchDesserts() {
  const { refetch } = useDesserts();
  await refetch();
}
