import React from "react";

interface AuctionProgressBarProps {
  startPrice: number;
  currentPrice: number;
  floorPrice: number;
  currencySymbol?: string;
  showLabels?: boolean;
}

export const AuctionProgressBar: React.FC<AuctionProgressBarProps> = ({
  startPrice,
  currentPrice,
  floorPrice,
  currencySymbol = "₴",
  showLabels = true,
}) => {
  const totalDescent = Math.max(0, startPrice - floorPrice);
  const currentDescent = Math.max(0, startPrice - currentPrice);
  const percentage =
    totalDescent > 0
      ? Math.min(100, Math.max(0, (currentDescent / totalDescent) * 100))
      : 0;

  const formatNumber = (num: number): string => {
    return Math.round(num)
      .toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  return (
    <div className="space-y-2">
      {showLabels && (
        <div className="flex justify-between text-[11px] font-mono text-muted-steel">
          <span>Стеля: {formatNumber(startPrice)} {currencySymbol}</span>
          <span>Підлога: {formatNumber(floorPrice)} {currencySymbol}</span>
        </div>
      )}

      <div className="w-full h-2 bg-gallery-canvas border border-hairline-border overflow-hidden">
        <div
          className="h-full bg-electric-blue transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex justify-between items-center text-[10px] font-mono text-muted-steel uppercase tracking-kicker">
        <span>ПРОГРЕС СПУСКУ: {Math.round(percentage)}%</span>
        <span>ЗУПИНКА НА ПІДЛОЗІ</span>
      </div>
    </div>
  );
};
