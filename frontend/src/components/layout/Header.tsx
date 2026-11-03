import React from "react";

interface HeaderProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab = "falling",
  onTabChange,
}) => {
  const navItems = [
    { id: "falling", label: "ПАДАЄ ЗАРАЗ" },
    { id: "how-it-works", label: "ЯК ЦЕ ПРАЦЮЄ" },
    { id: "ledger", label: "ПУБЛІЧНИЙ РЕЄСТР" },
    { id: "lookup", label: "ПОШУК КВИТАНЦІЇ" },
  ];

  return (
    <header className="sticky top-0 z-50 bg-pure-white border-b border-hairline-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => onTabChange?.("falling")}
            className="flex items-center text-carbon-pitch font-extrabold text-lg sm:text-xl tracking-wordmark uppercase select-none focus:outline-none"
          >
            VEILING
            <span className="inline-block w-3.5 h-3.5 bg-acid-lime ml-1.5 align-middle" />
          </button>
        </div>

        <nav className="hidden md:flex items-center space-x-8 text-xs font-bold tracking-wider">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange?.(item.id)}
                className={`transition-colors uppercase pb-1 ${
                  isActive
                    ? "text-carbon-pitch border-b-2 border-carbon-pitch"
                    : "text-muted-steel hover:text-carbon-pitch"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="flex items-center space-x-4">
          <button
            onClick={() => onTabChange?.("seller")}
            className="bg-electric-blue hover:bg-blue-700 text-pure-white px-4 py-2 text-xs font-bold tracking-wider uppercase transition-colors rounded-none"
          >
            СТВОРИТИ ЛОТ
          </button>
        </div>
      </div>

      <div className="md:hidden flex items-center overflow-x-auto space-x-4 px-4 sm:px-6 py-2 border-t border-hairline-border bg-gallery-canvas text-[11px] font-bold tracking-wider">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange?.(item.id)}
              className={`whitespace-nowrap transition-colors uppercase py-1 ${
                isActive
                  ? "text-carbon-pitch border-b-2 border-carbon-pitch"
                  : "text-muted-steel hover:text-carbon-pitch"
              }`}
            >
              {item.label}
            </button>
          );
        })}
      </div>
    </header>
  );
};
