import React from "react";
import { Clock } from "lucide-react";

interface DutchPriceTickerProps {
  currentPrice: number;
  startPrice: number;
  secondsRemaining?: number | null;
  size?: "sm" | "md" | "lg";
  currencySymbol?: string;
  showTimer?: boolean;
}

export const DutchPriceTicker: React.FC<DutchPriceTickerProps> = ({
  currentPrice,
  startPrice,
  secondsRemaining,
  size = "md",
  currencySymbol = "₴",
  showTimer = true,
}) => {
  const savingsPct =
    startPrice > 0
      ? Math.max(0, Math.round(((startPrice - currentPrice) / startPrice) * 100))
      : 0;

  const formatNumber = (num: number): string => {
    return Math.round(num)
      .toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  const formattedTimer =
    secondsRemaining != null && secondsRemaining >= 0
      ? `00:${secondsRemaining < 10 ? `0${secondsRemaining}` : secondsRemaining}`
      : null;

  const priceTextSize =
    size === "lg"
      ? "text-4xl sm:text-5xl lg:text-6xl"
      : size === "sm"
      ? "text-2xl sm:text-3xl"
      : "text-3xl sm:text-4xl";

  return (
    <div className="space-y-2">
      {showTimer && (
        <div className="flex items-center justify-between text-xs text-muted-steel font-mono">
          <span className="uppercase tracking-kicker">ПОТОЧНА ЦІНА</span>
          {formattedTimer && (
            <span className="flex items-center text-electric-blue font-bold tracking-wider">
              <Clock className="w-3.5 h-3.5 mr-1" />
              НАСТУПНИЙ КРОК ЧЕРЕЗ {formattedTimer}
            </span>
          )}
        </div>
      )}

      <div className="flex items-baseline flex-wrap gap-x-3 gap-y-1">
        <div
          className={`${priceTextSize} font-extrabold font-mono tracking-tight text-carbon-pitch tabular-nums`}
        >
          {formatNumber(currentPrice)} {currencySymbol}
        </div>
        {startPrice > currentPrice && (
          <div className="text-sm sm:text-base font-mono text-muted-steel line-through tabular-nums">
            {formatNumber(startPrice)} {currencySymbol}
          </div>
        )}
      </div>

      {savingsPct > 0 && (
        <div className="text-xs font-mono font-bold text-electric-blue uppercase tracking-wider">
          ПАДІННЯ ВІД СТЕЛІ: -{savingsPct}%
        </div>
      )}
    </div>
  );
};
