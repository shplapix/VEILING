import React, { useEffect, useState } from "react";
import { Order, Lot } from "../types";
import { getLedger } from "../api/orders";
import { listLots } from "../api/lots";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { ArrowRight, Clock, ShieldCheck, ShoppingBag } from "lucide-react";

interface LedgerPageProps {
  onSelectLot?: (lot: Lot) => void;
  onNavigateHome?: () => void;
}

export const LedgerPage: React.FC<LedgerPageProps> = ({
  onSelectLot,
  onNavigateHome,
}) => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [takenLots, setTakenLots] = useState<Lot[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [ledgerOrders, lots] = await Promise.all([
          getLedger().catch(() => []),
          listLots("TAKEN").catch(() => []),
        ]);
        setOrders(ledgerOrders);
        setTakenLots(lots);
      } catch {
        setOrders([]);
        setTakenLots([]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const formatNumber = (num: number): string => {
    return Math.round(num)
      .toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  const formatDate = (isoString?: string | null): string => {
    if (!isoString) {
      return "Нещодавно";
    }
    try {
      const date = new Date(isoString);
      return date.toLocaleString("uk-UA", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  const hasItems = orders.length > 0 || takenLots.length > 0;

  return (
    <div className="py-12 sm:py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
      <div className="max-w-3xl space-y-4">
        <div className="inline-flex items-center space-x-2 text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch">
          <span className="w-2.5 h-2.5 bg-acid-lime inline-block" />
          <span>ПУБЛІЧНИЙ РЕЄСТР ЗАКРИТИХ УГОД · RECENTLY TAKEN</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-carbon-pitch">
          Що насправді дав спуск
        </h1>
        <p className="text-base text-muted-steel leading-relaxed font-sans">
          Усі предмети в VEILING є унікальними екземплярами 1-of-1 і більше ніколи
          не повторяться. Ми публікуємо точні суми закріплення кожного лота —
          справжня прозорість без прихованих комісій.
        </p>
      </div>

      {isLoading ? (
        <div className="p-16 text-center bg-pure-white border border-hairline-border">
          <span className="font-mono text-xs uppercase tracking-kicker text-muted-steel">
            ЗАВАНТАЖЕННЯ ПУБЛІЧНОГО РЕЄСТРУ...
          </span>
        </div>
      ) : !hasItems ? (
        <div className="bg-pure-white border border-hairline-border p-12 text-center space-y-6">
          <ShoppingBag className="w-8 h-8 text-muted-steel mx-auto" />
          <div className="max-w-md mx-auto space-y-2">
            <h3 className="text-xl font-bold tracking-tight">
              Реєстр очікує перших угод
            </h3>
            <p className="text-xs text-muted-steel leading-relaxed font-sans">
              Усі представлені архівні речі зараз знаходяться у процесі падіння цін.
              Ви можете стати першим, хто зафіксує раритет.
            </p>
          </div>
          {onNavigateHome && (
            <Button variant="primary" size="lg" onClick={onNavigateHome}>
              ДИВИТИСЯ ЩО ПАДАЄ ЗАРАЗ
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-pure-white border border-hairline-border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-sans">
                <thead className="bg-gallery-canvas border-b border-hairline-border text-muted-steel font-mono uppercase text-[10px] tracking-kicker select-none">
                  <tr>
                    <th className="p-4 sm:px-6">Експонат</th>
                    <th className="p-4">Бренд / Сезон</th>
                    <th className="p-4">Час фіксації</th>
                    <th className="p-4 text-right">Фінальна ціна</th>
                    <th className="p-4 text-right">Падіння</th>
                    <th className="p-4 text-right">Дія</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hairline-border">
                  {orders.length > 0
                    ? orders.map((order) => {
                        const lot = order.lot;
                        const primaryImage =
                          lot?.images && lot.images.length > 0
                            ? [...lot.images].sort(
                                (a, b) => a.sort_order - b.sort_order
                              )[0]
                            : null;

                        return (
                          <tr
                            key={order.id}
                            className="hover:bg-gallery-canvas/40 transition-colors"
                          >
                            <td className="p-4 sm:px-6">
                              <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-gallery-canvas border border-hairline-border overflow-hidden shrink-0">
                                  {primaryImage ? (
                                    <img
                                      src={primaryImage.image_url}
                                      alt={lot?.title || "Archive lot"}
                                      onError={(e) => {
                                        const target = e.currentTarget as HTMLImageElement;
                                        const cleanUrl = primaryImage.image_url.split("?")[0];
                                        const filename = cleanUrl.split("/").pop();
                                        if (filename && !target.src.endsWith(`/lots/${filename}`)) {
                                          target.src = `/lots/${filename}`;
                                        }
                                      }}
                                      className="w-full h-full object-cover object-center"
                                    />
                                  ) : (
                                    <div className="w-full h-full flex items-center justify-center font-mono text-[10px] text-muted-steel">
                                      {lot?.brand || "VEILING"}
                                    </div>
                                  )}
                                </div>
                                <div className="min-w-0">
                                  <span className="font-bold text-carbon-pitch text-sm block truncate">
                                    {lot?.title || "Архівний лот"}
                                  </span>
                                  <span className="text-[11px] font-mono text-muted-steel block">
                                    {order.claim_code}
                                  </span>
                                </div>
                              </div>
                            </td>

                            <td className="p-4 text-muted-steel">
                              <span className="font-semibold text-carbon-pitch block">
                                {lot?.brand || "Архів"}
                              </span>
                              <span className="text-[11px] font-mono">
                                {lot ? `${lot.season} ${lot.year}` : "—"}
                              </span>
                            </td>

                            <td className="p-4 font-mono text-muted-steel whitespace-nowrap">
                              <div className="flex items-center gap-1.5">
                                <Clock className="w-3.5 h-3.5 text-muted-steel" />
                                <span>{formatDate(order.created_at)}</span>
                              </div>
                            </td>

                            <td className="p-4 font-mono font-bold text-right text-carbon-pitch text-sm tabular-nums whitespace-nowrap">
                              {formatNumber(order.final_price)} ₴
                            </td>

                            <td className="p-4 text-right whitespace-nowrap">
                              <Badge variant="lime">
                                -{order.savings_percentage}%
                              </Badge>
                            </td>

                            <td className="p-4 text-right whitespace-nowrap">
                              {lot && onSelectLot && (
                                <button
                                  type="button"
                                  onClick={() => onSelectLot(lot)}
                                  className="text-xs font-mono font-bold text-electric-blue hover:underline uppercase inline-flex items-center gap-1"
                                >
                                  <span>ПЕРЕГЛЯНУТИ</span>
                                  <ArrowRight className="w-3 h-3" />
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })
                    : takenLots.map((lot) => {
                        const primaryImage =
                          lot.images && lot.images.length > 0
                            ? [...lot.images].sort(
                                (a, b) => a.sort_order - b.sort_order
                              )[0]
                            : null;

                        const savings =
                          lot.start_price > 0 && lot.final_price
                            ? Math.round(
                                ((lot.start_price - lot.final_price) /
                                  lot.start_price) *
                                  100
                              )
                            : 0;

                        return (
                          <tr
                            key={lot.id}
                            className="hover:bg-gallery-canvas/40 transition-colors"
                          >
                            <td className="p-4 sm:px-6">
                              <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-gallery-canvas border border-hairline-border overflow-hidden shrink-0">
                                  {primaryImage ? (
                                    <img
                                      src={primaryImage.image_url}
                                      alt={lot.title}
                                      onError={(e) => {
                                        const target = e.currentTarget as HTMLImageElement;
                                        const cleanUrl = primaryImage.image_url.split("?")[0];
                                        const filename = cleanUrl.split("/").pop();
                                        if (filename && !target.src.endsWith(`/lots/${filename}`)) {
                                          target.src = `/lots/${filename}`;
                                        }
                                      }}
                                      className="w-full h-full object-cover object-center"
                                    />
                                  ) : (
                                    <div className="w-full h-full flex items-center justify-center font-mono text-[10px] text-muted-steel">
                                      {lot.brand}
                                    </div>
                                  )}
                                </div>
                                <div className="min-w-0">
                                  <span className="font-bold text-carbon-pitch text-sm block truncate">
                                    {lot.title}
                                  </span>
                                  <span className="text-[11px] font-mono text-muted-steel block">
                                    Розмір: {lot.tagged_size}
                                  </span>
                                </div>
                              </div>
                            </td>

                            <td className="p-4 text-muted-steel">
                              <span className="font-semibold text-carbon-pitch block">
                                {lot.brand}
                              </span>
                              <span className="text-[11px] font-mono">
                                {lot.season} {lot.year}
                              </span>
                            </td>

                            <td className="p-4 font-mono text-muted-steel whitespace-nowrap">
                              <div className="flex items-center gap-1.5">
                                <Clock className="w-3.5 h-3.5 text-muted-steel" />
                                <span>{formatDate(lot.taken_at)}</span>
                              </div>
                            </td>

                            <td className="p-4 font-mono font-bold text-right text-carbon-pitch text-sm tabular-nums whitespace-nowrap">
                              {formatNumber(lot.final_price ?? lot.current_price)} ₴
                            </td>

                            <td className="p-4 text-right whitespace-nowrap">
                              <Badge variant="lime">
                                -{savings}%
                              </Badge>
                            </td>

                            <td className="p-4 text-right whitespace-nowrap">
                              {onSelectLot && (
                                <button
                                  type="button"
                                  onClick={() => onSelectLot(lot)}
                                  className="text-xs font-mono font-bold text-electric-blue hover:underline uppercase inline-flex items-center gap-1"
                                >
                                  <span>ПЕРЕГЛЯНУТИ</span>
                                  <ArrowRight className="w-3 h-3" />
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="p-6 bg-pure-white border border-hairline-border flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-electric-blue shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch block">
                НЕЗМІННІСТЬ РЕЄСТРУ
              </span>
              <p className="text-xs text-muted-steel font-sans leading-relaxed">
                Кожне закріплення лота фіксується унікальним чек-кодом та стає
                частиною публічної історії цін будинку архівної моди VEILING.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
