export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          Vinted Optimizer
        </h1>
        <p className="text-center text-muted-foreground mb-8">
          Ottimizza le tue vendite su Vinted con l'intelligenza artificiale
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">📸 Analisi AI</h2>
            <p className="text-muted-foreground">
              Analisi automatica delle immagini per identificare prodotti e suggerire prezzi ottimali
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">📊 Dashboard</h2>
            <p className="text-muted-foreground">
              Gestione centralizzata delle vendite per te e la tua famiglia
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">🚚 Spedizioni</h2>
            <p className="text-muted-foreground">
              Integrazione multi-corriere con tracking automatico
            </p>
          </div>
        </div>
        <div className="mt-8 text-center">
          <a
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            Accedi alla Dashboard
          </a>
        </div>
      </div>
    </main>
  );
}
