import { createFileRoute } from '@tanstack/react-router'
import { useState } from "react"
import { DataTable } from "@/components/table/data-table";
import { columns } from "@/components/table/columns";
import type { DessertOut } from '@/lib/api'


export const Route = createFileRoute('/app/table-editor')({
    component: RouteComponent,
})



// Mock data for demonstration
const initialData: DessertOut[] = [
    {
        id: 1,
        name: "Chocolate Lava Cake",
        price: 12.99,
        description: "Rich chocolate cake with molten center, served with vanilla ice cream",
        leftInStock: 15,
    },
    {
        id: 2,
        name: "Tiramisu",
        price: 9.99,
        description: "Classic Italian dessert with coffee-soaked ladyfingers and mascarpone",
        leftInStock: 8,
    },
    {
        id: 3,
        name: "Crème Brûlée",
        price: 11.5,
        description: "Vanilla custard with caramelized sugar crust",
        leftInStock: 12,
    },
    {
        id: 4,
        name: "Strawberry Cheesecake",
        price: 10.99,
        description: "New York style cheesecake topped with fresh strawberries",
        leftInStock: 6,
    },
    {
        id: 5,
        name: "Apple Pie",
        price: 8.99,
        description: "Traditional apple pie with cinnamon and flaky crust",
        leftInStock: 20,
    },
    {
        id: 6,
        name: "Chocolate Mousse",
        price: 7.99,
        description: "Light and airy chocolate mousse with whipped cream",
        leftInStock: 0,
    },
]

export default function RouteComponent() {
    const [data, setData] = useState<DessertOut[]>(initialData)

    const updateData = (rowIndex: number, columnId: string, value: any) => {
        setData((old) =>
            old.map((row, index) => {
                if (index === rowIndex) {
                    return {
                        ...row,
                        [columnId]: value,
                    }
                }
                return row
            }),
        )
    }

    return (
        <div className="container mx-auto py-10">
            <div className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight">Dessert Menu</h1>
                <p className="text-muted-foreground">Manage your dessert inventory with inline editing capabilities</p>
            </div>
            <DataTable columns={columns} data={data} updateData={updateData} />
        </div>
    )
}
