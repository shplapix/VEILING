import React, { useCallback, useEffect, useState } from "react";
import { Lot, AuctionWsEvent } from "../types";
import { getLot } from "../api/lots";
import { useAuctionWs } from "../hooks/useAuctionWs";
import { PhotoGallery } from "../components/lot/PhotoGallery";
import { SpecsAccordion } from "../components/lot/SpecsAccordion";
import { DutchPriceTicker } from "../components/auction/DutchPriceTicker";
import { AuctionProgressBar } from "../components/auction/AuctionProgressBar";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { ArrowDownRight, ArrowLeft, CheckCircle2, ShieldCheck } from "lucide-react";

interface LotDetailPageProps {
  initialLot: Lot;
  onBack: () => void;
  onTake: (lot: Lot) => void;
  isTaking?: boolean;
  myClaimCode?: string;
}

export const LotDetailPage: React.FC<LotDetailPageProps> = ({
  initialLot,
  onBack,
  onTake,
  isTaking = false,
  myClaimCode,
}) => {
  const [lot, setLot] = useState<Lot>(initialLot);
  const [now, setNow] = useState<number>(Date.now());

  const handleWsEvent = useCallback(
    (event: AuctionWsEvent) => {
      if (event.lot_id !== lot.id) {
        return;
      }
      if (event.event === "PRICE_TICK") {
        setLot((prev) => ({
          ...prev,
          current_price: event.current_price,
          next_drop_at: event.next_drop_at,
        }));
      } else if (event.event === "LOT_TAKEN") {
        setLot((prev) => ({
          ...prev,
          status: "TAKEN",
          final_price: event.final_price,
          taken_at: event.taken_at,
        }));
      } else if (event.event === "LOT_EXPIRED") {
        setLot((prev) => ({
          ...prev,
          status: "EXPIRED",
          current_price: event.floor_price,
        }));
      }
    },
    [lot.id]
  );

  useAuctionWs(handleWsEvent);

  useEffect(() => {
    setLot(initialLot);
    getLot(initialLot.id)
      .then((fresh) => {
        if (fresh) {
          setLot(fresh);
        }
      })
      .catch(() => {});
  }, [initialLot]);

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(Date.now());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const calculateRemainingSeconds = (nextDropAt?: string | null): number | null => {
    if (!nextDropAt) {
      return null;
    }
    const target = new Date(nextDropAt).getTime();
    const diff = Math.max(0, Math.floor((target - now) / 1000));
    return diff;
  };

  const formatNumber = (num: number): string => {
    return Math.round(num)
      .toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  const isTaken = lot.status === "TAKEN";
  const isExpired = lot.status === "EXPIRED";
  const isActive = lot.status === "ACTIVE";
  const secondsRemaining = calculateRemainingSeconds(lot.next_drop_at);

  return (
    <div className="py-8 sm:py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <div>
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 text-xs font-mono font-bold uppercase tracking-kicker text-muted-steel hover:text-carbon-pitch transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>НАЗАД ДО КАТАЛОГУ</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
        <div className="lg:col-span-7 space-y-8">
          <PhotoGallery images={lot.images} title={lot.title} />

          <div className="bg-pure-white border border-hairline-border p-6 space-y-4">
            <div className="text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch">
              МУЗЕЙНИЙ ПРОВЕНАНС ТА АВТЕНТИЧНІСТЬ
            </div>
            <p className="text-xs sm:text-sm text-carbon-pitch font-sans leading-relaxed">
              Кожен експонат у домі VEILING проходить фізичну перевірку автентичності
              швів, волокон, маркування фурнітури та ярликів відповідності сезону.
            </p>
            <div className="flex flex-wrap gap-4 pt-2 border-t border-hairline-border text-xs font-mono text-muted-steel">
              <div>
                МІСТО: <span className="text-carbon-pitch font-bold">{lot.seller_location}</span>
              </div>
              <div>
                ДИЗАЙНЕР: <span className="text-carbon-pitch font-bold">{lot.designer}</span>
              </div>
              <div>
                СТАН: <span className="text-carbon-pitch font-bold">{lot.condition_rating}/10</span>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-5 space-y-6">
          <div className="bg-pure-white border border-hairline-border p-6 sm:p-8 space-y-6">
            <div className="space-y-3 pb-6 border-b border-hairline-border">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold uppercase tracking-kicker text-muted-steel">
                  АРХІВ {lot.category} · {lot.brand}
                </span>
                {isActive ? (
                  <Badge variant="blue">LIVE СПУСК</Badge>
                ) : isTaken ? (
                  <Badge variant="lime">
                    {myClaimCode ? "ЗАКРІПЛЕНО ЗА ВАМИ" : "ЗАБРАНО"}
                  </Badge>
                ) : isExpired ? (
                  <Badge variant="carbon">ПІДЛОГА</Badge>
                ) : lot.status === "SCHEDULED" ? (
                  <Badge variant="carbon">СКОРО</Badge>
                ) : lot.status === "CANCELLED" ? (
                  <Badge variant="carbon">СКАСОВАНО</Badge>
                ) : (
                  <Badge variant="carbon">В РЕЗЕРВІ</Badge>
                )}
              </div>

              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-carbon-pitch">
                {lot.title}
              </h1>

              <div className="text-xs font-mono text-muted-steel">
                {lot.collection_name && `Колекція "${lot.collection_name}" · `}
                {lot.season} {lot.year} · Розмір {lot.tagged_size}
                {lot.fits_like ? ` (${lot.fits_like})` : ""}
              </div>
            </div>

            <div className="space-y-6">
              <DutchPriceTicker
                currentPrice={lot.current_price}
                startPrice={lot.start_price}
                secondsRemaining={isActive ? secondsRemaining : null}
                size="lg"
              />

              <AuctionProgressBar
                startPrice={lot.start_price}
                currentPrice={lot.current_price}
                floorPrice={lot.floor_price}
              />

              <div className="grid grid-cols-2 gap-3 pt-2 text-xs font-mono">
                <div className="p-3 bg-gallery-canvas border border-hairline-border">
                  <span className="text-muted-steel text-[10px] uppercase block">
                    КРОК ПАДІННЯ
                  </span>
                  <span className="font-bold text-carbon-pitch">
                    -{formatNumber(lot.step_amount)} ₴
                  </span>
                </div>
                <div className="p-3 bg-gallery-canvas border border-hairline-border">
                  <span className="text-muted-steel text-[10px] uppercase block">
                    ІНТЕРВАЛ
                  </span>
                  <span className="font-bold text-carbon-pitch">
                    кожні {lot.interval_seconds} сек
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2 space-y-3">
              {isActive ? (
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full py-4 text-sm font-bold flex items-center justify-center space-x-2 tracking-wider uppercase"
                  disabled={isTaking}
                  onClick={() => onTake(lot)}
                >
                  <ArrowDownRight className="w-5 h-5" />
                  <span>
                    {isTaking
                      ? "ФІКСАЦІЯ..."
                      : `ЗАБРАТИ ЗА ${formatNumber(lot.current_price)} ₴`}
                  </span>
                </Button>
              ) : isTaken ? (
                <div className="p-4 bg-gallery-canvas border border-hairline-border text-xs font-mono space-y-2">
                  <div className="flex items-center gap-2 text-carbon-pitch font-bold text-sm">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    <span>
                      {myClaimCode
                        ? "ВИ УСПІШНО ЗАБРАЛИ ЕКСПОНАТ"
                        : `ЗАБРАНО ЗА ${formatNumber(lot.final_price ?? lot.current_price)} ₴`}
                    </span>
                  </div>
                  <div className="text-muted-steel text-xs font-sans leading-relaxed">
                    {myClaimCode ? (
                      <div>
                        Експонат закріплено за вами. Ваш унікальний чек-код:{" "}
                        <span className="text-carbon-pitch font-mono font-bold select-all">
                          {myClaimCode}
                        </span>
                        . Ви можете перевірити статус у розділі «Пошук квитанції».
                      </div>
                    ) : (
                      "Цю унікальну річ уже зафіксував інший покупець. Вона більше не з'явиться в каталозі, оскільки існує в єдиному екземплярі."
                    )}
                  </div>
                </div>
              ) : isExpired ? (
                <Button
                  variant="outline"
                  size="lg"
                  className="w-full opacity-60 cursor-not-allowed"
                  disabled
                >
                  СПУСК ЗУПИНЕНО НА ПІДЛОЗІ
                </Button>
              ) : lot.status === "SCHEDULED" ? (
                <Button
                  variant="outline"
                  size="lg"
                  className="w-full opacity-70 cursor-not-allowed"
                  disabled
                >
                  СКОРО НА СПУСКУ
                </Button>
              ) : lot.status === "CANCELLED" ? (
                <Button
                  variant="outline"
                  size="lg"
                  className="w-full opacity-60 cursor-not-allowed"
                  disabled
                >
                  СКАСОВАНО
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="lg"
                  className="w-full opacity-70 cursor-not-allowed"
                  disabled
                >
                  ЕКСПОНАТ У РЕЗЕРВІ
                </Button>
              )}

              <div className="flex items-start gap-2 pt-2 text-[11px] font-mono text-muted-steel">
                <ShieldCheck className="w-4 h-4 text-carbon-pitch shrink-0 mt-0.5" />
                <span>
                  Атомарна фіксація в PostgreSQL. Перший клік закріплює річ назавжди.
                  Без акаунтів: квитанція з чек-кодом видається миттєво.
                </span>
              </div>
            </div>
          </div>

          <SpecsAccordion lot={lot} />
        </div>
      </div>
    </div>
  );
};
