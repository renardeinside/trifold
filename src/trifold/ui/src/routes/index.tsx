import { createFileRoute } from '@tanstack/react-router';
import { Link } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Database, Briefcase, Users } from 'lucide-react';
import Logo from '@/assets/Logo';
import { ModeToggle } from '@/components/mode-toggle';
import { version } from '@/lib/api';

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

      <FadeIn>
        <div className="flex flex-col items-center mb-8">
          <Logo className="h-64 w-64 mb-4 drop-shadow-lg" />
          <h1 className="text-5xl font-bold text-accent-foreground tracking-tight">
            Cloud Data Hub on <AuroraText>Databricks</AuroraText>
          </h1>
        </div>
      </FadeIn>

      <p className="z-10 mt-4 text-center max-w-2xl">
        <span className="text-lg text-accent-foreground/50 leading-0 tracking-tight">
          Some things are still under construction, but you can already do something with it.
        </span>
      </p>

      <div className="z-10 mt-8 flex gap-6">
        <Link to="/app/datasets">
          <Button className="flex items-center gap-2 cursor-pointer" size="lg">
            <Database size={20} />
            Datasets
          </Button>
        </Link>
        <Link to="/app/use-cases">
          <Button className="flex items-center gap-2 cursor-pointer" size="lg">
            <Briefcase size={20} />
            Use Cases
          </Button>
        </Link>
        <Link to="/app/providers">
          <Button className="flex items-center gap-2 cursor-pointer" size="lg">
            <Users size={20} />
            Providers
          </Button>
        </Link>
      </div>
    </div>
  );
}
