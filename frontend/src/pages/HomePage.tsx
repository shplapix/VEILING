import React, { useCallback, useEffect, useState } from "react";
import { Lot, AuctionWsEvent } from "../types";
import { listLots } from "../api/lots";
import { useAuctionWs } from "../hooks/useAuctionWs";
import { LiveAuctionCard } from "../components/auction/LiveAuctionCard";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { ArrowDown, Radio } from "lucide-react";

interface HomePageProps {
  onSelectLot: (lot: Lot) => void;
  onTakeLot: (lot: Lot) => void;
  onNavigateSeller: () => void;
  onNavigateHowItWorks: () => void;
  takingLotId?: string | null;
  lastTakenLot?: { lotId: string; finalPrice?: number; takenAt?: string } | null;
}

export const HomePage: React.FC<HomePageProps> = ({
  onSelectLot,
  onTakeLot,
  onNavigateSeller,
  onNavigateHowItWorks,
  takingLotId,
  lastTakenLot,
}) => {
  const [lots, setLots] = useState<Lot[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [now, setNow] = useState<number>(Date.now());

  const handleWsEvent = useCallback((event: AuctionWsEvent) => {
    if (event.event === "PRICE_TICK") {
      setLots((prev) =>
        prev.map((l) =>
          l.id === event.lot_id
            ? {
                ...l,
                current_price: event.current_price,
                next_drop_at: event.next_drop_at,
              }
            : l
        )
      );
    } else if (event.event === "LOT_TAKEN") {
      setLots((prev) =>
        prev.map((l) =>
          l.id === event.lot_id
            ? {
                ...l,
                status: "TAKEN",
                final_price: event.final_price,
                taken_at: event.taken_at,
              }
            : l
        )
      );
    } else if (event.event === "LOT_EXPIRED") {
      setLots((prev) =>
        prev.map((l) =>
          l.id === event.lot_id
            ? {
                ...l,
                status: "EXPIRED",
                current_price: event.floor_price,
              }
            : l
        )
      );
    }
  }, []);

  const { isConnected } = useAuctionWs(handleWsEvent);

  const fetchLots = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await listLots();
      setLots(data);
    } catch {
      setLots([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLots();
  }, [fetchLots]);

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(Date.now());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!lastTakenLot) {
      return;
    }
    setLots((prev) =>
      prev.map((l) =>
        l.id === lastTakenLot.lotId
          ? {
              ...l,
              status: "TAKEN",
              final_price: lastTakenLot.finalPrice ?? l.current_price,
              taken_at: lastTakenLot.takenAt ?? new Date().toISOString(),
            }
          : l
      )
    );
  }, [lastTakenLot]);

  const activeLots = lots.filter((l) => l.status === "ACTIVE");
  const otherLots = lots.filter((l) => l.status !== "ACTIVE");
  const displayLots = activeLots.length > 0 ? activeLots : lots;

  const calculateRemainingSeconds = (nextDropAt?: string | null): number | null => {
    if (!nextDropAt) {
      return null;
    }
    const target = new Date(nextDropAt).getTime();
    const diff = Math.max(0, Math.floor((target - now) / 1000));
    return diff;
  };

  const scrollToCatalog = () => {
    const catalogElement = document.getElementById("falling-now-catalog");
    if (catalogElement) {
      catalogElement.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="space-y-16">
      <section className="border-b border-hairline-border bg-pure-white py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <div className="inline-flex items-center space-x-2 text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch mb-4">
              <span className="w-2.5 h-2.5 bg-acid-lime inline-block" />
              <span>ГОЛЛАНДСЬКИЙ АУКЦІОН · ЦІНА ПАДАЄ НА ТАЙМЕРІ</span>
            </div>
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-hero leading-[1.05] mb-6">
              The price only goes <span className="text-electric-blue">down.</span>
            </h1>
            <p className="text-base sm:text-lg text-muted-steel leading-relaxed font-sans mb-8">
              Зворотний відлік, за яким ви спостерігаєте, а не аукціон, який ви
              можете програти. У кожен момент є лише одна ціна, і вона належить тому,
              хто забере її першим.
            </p>
            <div className="flex flex-wrap items-center gap-4">
              <Button variant="primary" size="lg" onClick={scrollToCatalog}>
                <span className="flex items-center gap-2">
                  <span>ДИВИТИСЯ ЩО ПАДАЄ ЗАРАЗ</span>
                  <ArrowDown className="w-4 h-4" />
                </span>
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={onNavigateHowItWorks}
              >
                ЯК ПРАЦЮЄ СПУСК
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section
        id="falling-now-catalog"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 scroll-mt-24"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-4 border-b border-hairline-border">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                Падає прямо зараз
              </h2>
              {isConnected ? (
                <span className="inline-flex items-center gap-1.5 text-[11px] font-mono text-emerald-600 font-bold uppercase tracking-wider bg-emerald-50 px-2 py-0.5 border border-emerald-200">
                  <Radio className="w-3 h-3 animate-pulse" />
                  LIVE СИНХРОНІЗАЦІЯ
                </span>
              ) : (
                <span className="text-[11px] font-mono text-muted-steel tracking-wider bg-gallery-canvas px-2 py-0.5 border border-hairline-border">
                  ПІДКЛЮЧЕННЯ...
                </span>
              )}
            </div>
            <p className="text-xs text-muted-steel font-mono mt-1 uppercase tracking-kicker">
              {activeLots.length}{" "}
              {activeLots.length === 1 ? "АКТИВНИЙ СПУСК" : "АКТИВНИХ СПУСКІВ"}{" "}
              У РЕАЛЬНОМУ ЧАСІ
            </p>
          </div>
          <Badge variant="blue">LIVE ТРАНСЛЯЦІЯ</Badge>
        </div>

        {isLoading ? (
          <div className="p-16 text-center bg-pure-white border border-hairline-border">
            <span className="font-mono text-xs uppercase tracking-kicker text-muted-steel">
              ЗАВАНТАЖЕННЯ АКТИВНОГО КАТАЛОГУ...
            </span>
          </div>
        ) : displayLots.length === 0 ? (
          <div className="bg-pure-white border border-hairline-border p-12 text-center space-y-6">
            <div className="w-3 h-3 bg-acid-lime mx-auto" />
            <div className="max-w-md mx-auto space-y-2">
              <h3 className="text-xl font-bold tracking-tight">
                Зараз немає активних спусків
              </h3>
              <p className="text-xs text-muted-steel leading-relaxed font-sans">
                Усі раритети розібрано, або нові аукціони ще готуються до відкриття.
                Ви можете виставити власний культовий експонат.
              </p>
            </div>
            <Button variant="primary" size="lg" onClick={onNavigateSeller}>
              СТВОРИТИ ЛОТ
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {displayLots.map((lot) => (
              <LiveAuctionCard
                key={lot.id}
                lot={lot}
                secondsRemaining={calculateRemainingSeconds(lot.next_drop_at)}
                onSelect={onSelectLot}
                onTake={onTakeLot}
                isTaking={takingLotId === lot.id}
              />
            ))}
          </div>
        )}

        {activeLots.length > 0 && otherLots.length > 0 && (
          <div className="mt-16 pt-8 border-t border-hairline-border space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold tracking-tight">
                Нещодавні архівні експонати
              </h3>
              <span className="text-xs font-mono text-muted-steel uppercase tracking-kicker">
                ЗАКРИТІ СПУСКИ
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {otherLots.map((lot) => (
                <LiveAuctionCard
                  key={lot.id}
                  lot={lot}
                  onSelect={onSelectLot}
                  onTake={onTakeLot}
                />
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-t border-hairline-border pt-16">
          <div className="max-w-xl mb-12">
            <span className="text-xs font-mono text-electric-blue font-bold tracking-kicker uppercase block mb-2">
              МЕХАНІКА АУКЦІОНУ
            </span>
            <h2 className="text-3xl font-extrabold tracking-tight">
              Як працює голландський спуск
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-pure-white border border-hairline-border p-8">
              <div className="text-xs font-mono text-electric-blue font-bold tracking-kicker mb-3">
                01 / СТЕЛЯ ЦІНИ
              </div>
              <h3 className="text-lg font-bold mb-2">Відкриття на піку</h3>
              <p className="text-xs text-muted-steel leading-relaxed font-sans">
                Кожен архівний лот відкривається на максимальній оціночній вартості
                раритету. Це максимальна межа, вище якої ціна ніколи не підніметься.
              </p>
            </div>
            <div className="bg-pure-white border border-hairline-border p-8">
              <div className="text-xs font-mono text-electric-blue font-bold tracking-kicker mb-3">
                02 / СПУСК ПО ТАЙМЕРУ
              </div>
              <h3 className="text-lg font-bold mb-2">Дискретне падіння</h3>
              <p className="text-xs text-muted-steel leading-relaxed font-sans">
                Кожні 60 секунд ціна автоматично падає на фіксований крок. Публічний
                таймер відраховує секунди до наступного зниження.
              </p>
            </div>
            <div className="bg-pure-white border border-hairline-border p-8">
              <div className="text-xs font-mono text-electric-blue font-bold tracking-kicker mb-3">
                03 / ЗАБРАТИ В МОМЕНТ
              </div>
              <h3 className="text-lg font-bold mb-2">Миттєва фіксація</h3>
              <p className="text-xs text-muted-steel leading-relaxed font-sans">
                Перший покупець, який натисне «Забрати», закріплює експонат за собою
                за поточною ціною. Аукціон завершується миттєво.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-carbon-pitch text-pure-white py-16 border-t border-hairline-border/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-8">
          <div>
            <span className="text-acid-lime text-xs font-mono font-bold tracking-kicker uppercase block mb-2">
              ДЛЯ ВЛАСНИКІВ АРХІВУ
            </span>
            <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Маєте раритет, вартий красивого падіння?
            </h3>
            <p className="text-xs text-muted-steel max-w-xl mt-2 font-sans">
              VEILING забезпечує прямий доступ до колекціонерів світового рівня без
              виснажливого очікування.
            </p>
          </div>
          <Button variant="accent" size="lg" onClick={onNavigateSeller}>
            СТВОРИТИ ЛОТ
          </Button>
        </div>
      </section>
    </div>
  );
};
