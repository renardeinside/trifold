import { createFileRoute, Link } from '@tanstack/react-router';
import Logo from '@/assets/Logo';
import { ModeToggle } from '@/components/mode-toggle';
import { AuroraText } from '@/components/magicui/aurora-text';
import { Button } from '@/components/ui/button';
import { version } from '@/lib/api';
import { Table } from 'lucide-react';

export const Route = createFileRoute('/')({
    preload: true,
    loader: async () => {
        return (await version()).data.version;
    },
    component: () => <Landing />,
});

function Landing() {
    const version = Route.useLoaderData();

    return (
        <div className="relative flex flex-col items-center justify-center h-screen px-4">
            {/* Theme toggle in top right corner */}
            <div className="absolute top-4 right-4 z-20">
                <ModeToggle />
            </div>

            {/* Version badge in bottom right corner */}
            <div className="absolute bottom-1 left-1 z-20 font-mono text-xs">
                <span className="text-accent-foreground/50">App version: {version}</span>
            </div>

            <div className="flex flex-col items-center mb-8">
                <Logo className="h-64 w-64 mb-4 drop-shadow-lg" />
                <h1 className="text-5xl font-bold text-accent-foreground tracking-tight mb-8">
                    Full Stack Data App on <AuroraText>Databricks</AuroraText>
                </h1>
                
                <Link to="/app/table-editor">
                    <Button size="lg" className="flex items-center gap-2">
                        <Table className="h-5 w-5" />
                        Edit Table
                    </Button>
                </Link>
            </div>


        </div>
    );
}
