import React from "react";
import { ArrowDownRight, CheckCircle2, Clock } from "lucide-react";
import { Lot } from "../../types";
import { DutchPriceTicker } from "./DutchPriceTicker";
import { AuctionProgressBar } from "./AuctionProgressBar";
import { Button } from "../ui/Button";

interface LiveAuctionCardProps {
  lot: Lot;
  secondsRemaining?: number | null;
  onSelect?: (lot: Lot) => void;
  onTake?: (lot: Lot) => void;
  isTaking?: boolean;
}

export const LiveAuctionCard: React.FC<LiveAuctionCardProps> = ({
  lot,
  secondsRemaining,
  onSelect,
  onTake,
  isTaking = false,
}) => {
  const isTaken = lot.status === "TAKEN";
  const isExpired = lot.status === "EXPIRED";
  const isActive = lot.status === "ACTIVE";

  const primaryImage =
    lot.images && lot.images.length > 0
      ? [...lot.images].sort((a, b) => a.sort_order - b.sort_order)[0]
      : null;

  const formatNumber = (num: number): string => {
    return Math.round(num)
      .toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  const formattedTimer =
    secondsRemaining != null && secondsRemaining >= 0
      ? `${Math.floor(secondsRemaining / 60)
          .toString()
          .padStart(2, "0")}:${(secondsRemaining % 60)
          .toString()
          .padStart(2, "0")}`
      : null;

  return (
    <div className="bg-pure-white border border-hairline-border flex flex-col justify-between transition-colors hover:border-carbon-pitch/30 group">
      <div>
        <div
          className="relative aspect-[4/3] bg-gallery-canvas border-b border-hairline-border overflow-hidden cursor-pointer"
          onClick={() => onSelect?.(lot)}
        >
          <div className="absolute top-0 left-0 z-10">
            {isTaken ? (
              <div className="bg-acid-lime text-carbon-pitch font-mono font-bold text-xs uppercase px-3 py-1 tracking-wider">
                ЗАБРАНО
              </div>
            ) : isExpired ? (
              <div className="bg-carbon-pitch text-pure-white font-mono font-bold text-xs uppercase px-3 py-1 tracking-wider">
                ДОСЯГНУТО ПІДЛОГИ
              </div>
            ) : (
              <div className="bg-electric-blue text-pure-white font-mono font-bold text-xs uppercase px-3 py-1 flex items-center gap-1.5 tracking-wider">
                <span className="w-1.5 h-1.5 bg-acid-lime inline-block animate-pulse" />
                <span>ПАДАЄ ЗАРАЗ</span>
              </div>
            )}
          </div>

          {primaryImage ? (
            <img
              src={primaryImage.image_url}
              alt={lot.title}
              className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center select-none bg-gallery-canvas">
              <span className="text-xs font-mono text-muted-steel uppercase tracking-kicker block mb-1">
                {lot.brand}
              </span>
              <span className="text-base font-extrabold text-carbon-pitch tracking-tight">
                {lot.title}
              </span>
            </div>
          )}

          {isActive && formattedTimer && (
            <div className="absolute bottom-2 right-2 bg-carbon-pitch/85 backdrop-blur-sm text-pure-white font-mono text-[11px] px-2.5 py-1 flex items-center gap-1.5 border border-pure-white/10">
              <Clock className="w-3 h-3 text-acid-lime" />
              <span>ДО ПАДІННЯ: {formattedTimer}</span>
            </div>
          )}
        </div>

        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between text-[11px] font-mono text-muted-steel uppercase tracking-kicker">
            <span>АРХІВ {lot.category}</span>
            <span>{lot.season} {lot.year}</span>
          </div>

          <div
            className="cursor-pointer"
            onClick={() => onSelect?.(lot)}
          >
            <h3 className="text-lg font-bold text-carbon-pitch tracking-tight hover:text-electric-blue transition-colors">
              {lot.title}
            </h3>
            <p className="text-xs text-muted-steel mt-1 font-mono">
              Розмір: {lot.tagged_size} {lot.fits_like ? `(${lot.fits_like})` : ""} · Стан: {lot.condition_rating}/10
            </p>
          </div>

          <div className="pt-2 border-t border-hairline-border">
            <DutchPriceTicker
              currentPrice={lot.current_price}
              startPrice={lot.start_price}
              secondsRemaining={secondsRemaining}
              size="md"
              showTimer={false}
            />
          </div>

          <div className="pt-2">
            <AuctionProgressBar
              startPrice={lot.start_price}
              currentPrice={lot.current_price}
              floorPrice={lot.floor_price}
            />
          </div>
        </div>
      </div>

      <div className="p-6 pt-0 space-y-2">
        {isTaken ? (
          <div className="p-3 bg-gallery-canvas border border-hairline-border text-xs font-mono space-y-1">
            <div className="flex items-center gap-1.5 text-carbon-pitch font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>ЗАБРАНО ЗА {formatNumber(lot.final_price ?? lot.current_price)} ₴</span>
            </div>
            <div className="text-[11px] text-muted-steel">
              Річ закріплена за покупцем. Повтор неможливий.
            </div>
          </div>
        ) : isExpired ? (
          <Button
            variant="outline"
            size="lg"
            className="w-full opacity-60 cursor-not-allowed"
            disabled
          >
            СПУСК ЗАВЕРШЕНО
          </Button>
        ) : (
          <Button
            variant="primary"
            size="lg"
            className="w-full flex items-center justify-center space-x-2"
            disabled={isTaking}
            onClick={() => onTake ? onTake(lot) : onSelect?.(lot)}
          >
            <ArrowDownRight className="w-4 h-4" />
            <span>
              {isTaking
                ? "ФІКСАЦІЯ..."
                : `ЗАБРАТИ ЗА ${formatNumber(lot.current_price)} ₴`}
            </span>
          </Button>
        )}

        <div className="text-[10px] font-mono text-muted-steel text-center uppercase tracking-kicker">
          ЦІНА ТІЛЬКИ ПАДАЄ · ПЕРШИЙ ХТО ЗАБЕРЕ — ОТРИМУЄ РІЧ
        </div>
      </div>
    </div>
  );
};
