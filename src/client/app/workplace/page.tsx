import ProposalFigureWorkspace, {
  type FigureView,
  type ThemeMode,
} from "@/components/workplace/ProposalFigureWorkspace";

type WorkplacePageProps = {
  searchParams?: Promise<{
    figure?: string;
    theme?: string;
  }>;
};

function parseInitialFigure(value: string | undefined): FigureView {
  if (value === "cross" || value === "downstream" || value === "within") return value;
  return "within";
}

function parseInitialTheme(value: string | undefined): ThemeMode {
  return value === "dark" ? "dark" : "light";
}

export default async function WorkplacePage({ searchParams }: WorkplacePageProps) {
  const params = await searchParams;
  return (
    <ProposalFigureWorkspace
      initialFigure={parseInitialFigure(params?.figure)}
      initialTheme={parseInitialTheme(params?.theme)}
    />
  );
}
