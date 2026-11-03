import React, { useState } from "react";
import { Order, Lot } from "../types";
import { lookupOrder } from "../api/orders";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Search,
  ShieldCheck,
  Truck,
} from "lucide-react";

interface ClaimLookupPageProps {
  initialCode?: string;
  onSelectLot?: (lot: Lot) => void;
}

export const ClaimLookupPage: React.FC<ClaimLookupPageProps> = ({
  initialCode = "",
  onSelectLot,
}) => {
  const [code, setCode] = useState<string>(initialCode);
  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const formatNumber = (num: number): string => {
    return Math.round(num)
      .toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  const formatDate = (isoString: string): string => {
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

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    const clean = code.trim().toUpperCase();
    if (!clean) {
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    setOrder(null);

    try {
      const foundOrder = await lookupOrder(clean);
      setOrder(foundOrder);
    } catch (err: unknown) {
      const detail =
        typeof err === "object" && err !== null && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data
              ?.detail
          : null;
      setErrorMessage(
        detail ||
          "Замовлення за вказаним чек-кодом не знайдено. Перевірте формат коду."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const primaryImage =
    order?.lot?.images && order.lot.images.length > 0
      ? [...order.lot.images].sort((a, b) => a.sort_order - b.sort_order)[0]
      : null;

  return (
    <div className="py-12 sm:py-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
      <div className="max-w-2xl space-y-3">
        <div className="inline-flex items-center space-x-2 text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch">
          <span className="w-2.5 h-2.5 bg-acid-lime inline-block" />
          <span>БЕЗАККАУНТНИЙ ДОСТУП ДО ПРИДБАНЬ</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-carbon-pitch">
          Знайдіть те, що ви забрали
        </h1>
        <p className="text-sm text-muted-steel leading-relaxed font-sans">
          Тут немає обов'язкових акаунтів чи паролів. Введіть криптографічний
          чек-код із вашої квитанції, щоб отримати повну інформацію про замовлення.
        </p>
      </div>

      <div className="bg-pure-white border border-hairline-border p-6 sm:p-8 space-y-6">
        <form onSubmit={handleLookup} className="space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch mb-2">
              КОД КВИТАНЦІЇ ЗАКРІПЛЕННЯ (CLAIM CODE)
            </label>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                placeholder="V-2026-XXXX-XXXX-XXXX"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                className="flex-1 border border-hairline-border px-4 py-3 font-mono text-sm uppercase tracking-wider focus:outline-none focus:border-carbon-pitch rounded-none"
              />
              <Button
                type="submit"
                variant="primary"
                size="lg"
                disabled={isLoading}
                className="flex items-center justify-center space-x-2 px-8 py-3"
              >
                <Search className="w-4 h-4" />
                <span>{isLoading ? "ПОШУК..." : "ПОШУК КВИТАНЦІЇ"}</span>
              </Button>
            </div>
          </div>
          <span className="text-[11px] font-mono text-muted-steel block">
            ПРИКЛАД ФОРМАТУ: V-2026-XXXX-XXXX-XXXX (16 СИМВОЛІВ У ВЕРХНЬОМУ РЕГІСТРІ)
          </span>
        </form>

        {errorMessage && (
          <div className="p-4 bg-gallery-canvas border border-hairline-border space-y-1">
            <div className="flex items-center gap-2 text-carbon-pitch font-bold text-xs">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <p className="text-[11px] text-muted-steel font-sans pl-6">
              Переконайтеся, що код введено без помилок або зайвих символів.
            </p>
          </div>
        )}

        {order && (
          <div className="pt-6 border-t border-hairline-border space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gallery-canvas p-4 border border-hairline-border">
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <div>
                  <span className="text-xs font-mono font-bold text-carbon-pitch uppercase tracking-wider block">
                    КВИТАНЦІЯ ЗНАЙДЕНА ТА ПІДТВЕРДЖЕНА
                  </span>
                  <span className="text-[11px] font-mono text-muted-steel">
                    ЧЕК-КОД: {order.claim_code}
                  </span>
                </div>
              </div>
              <Badge variant="lime">СТАТУС: {order.status}</Badge>
            </div>

            {order.lot && (
              <div className="flex flex-col sm:flex-row gap-6 p-4 bg-pure-white border border-hairline-border">
                <div className="w-full sm:w-40 aspect-square bg-gallery-canvas border border-hairline-border overflow-hidden shrink-0">
                  {primaryImage ? (
                    <img
                      src={primaryImage.image_url}
                      alt={order.lot.title}
                      className="w-full h-full object-cover object-center"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs font-mono text-muted-steel text-center p-3">
                      {order.lot.brand}
                    </div>
                  )}
                </div>

                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between text-xs font-mono text-muted-steel uppercase tracking-kicker">
                    <span>АРХІВ {order.lot.category}</span>
                    <span>{order.lot.season} {order.lot.year}</span>
                  </div>

                  <div>
                    <h3 className="text-xl font-extrabold text-carbon-pitch tracking-tight">
                      {order.lot.title}
                    </h3>
                    <p className="text-xs text-muted-steel font-mono mt-0.5">
                      Розмір: {order.lot.tagged_size} {order.lot.fits_like ? `(${order.lot.fits_like})` : ""} · Стан {order.lot.condition_rating}/10
                    </p>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-3 border-t border-hairline-border text-xs font-mono">
                    <div>
                      <span className="text-muted-steel text-[10px] uppercase block">
                        ФІКСОВАНА ЦІНА
                      </span>
                      <span className="text-base font-bold text-carbon-pitch">
                        {formatNumber(order.final_price)} ₴
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-steel text-[10px] uppercase block">
                        ПАДІННЯ ВІД СТЕЛІ
                      </span>
                      <span className="text-base font-bold text-electric-blue">
                        -{order.savings_percentage}%
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-steel text-[10px] uppercase block">
                        ЕКОНОМІЯ
                      </span>
                      <span className="text-base font-bold text-carbon-pitch">
                        {formatNumber(order.savings_from_ceiling)} ₴
                      </span>
                    </div>
                  </div>

                  {onSelectLot && (
                    <div className="pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onSelectLot(order.lot!)}
                        className="flex items-center gap-1.5"
                      >
                        <span>ПЕРЕГЛЯНУТИ ЕКСПОНАТ</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-4 bg-gallery-canvas border border-hairline-border space-y-2">
                <div className="flex items-center gap-2 text-carbon-pitch font-bold uppercase tracking-kicker">
                  <Truck className="w-4 h-4 text-carbon-pitch" />
                  <span>ДОСТАВКА ТА АДРЕСА</span>
                </div>
                <div className="text-muted-steel space-y-1">
                  <div>
                    Одержувач:{" "}
                    <span className="text-carbon-pitch font-bold">
                      {order.shipping_address?.recipient_name || "Не вказано"}
                    </span>
                  </div>
                  <div>
                    Місто:{" "}
                    <span className="text-carbon-pitch font-bold">
                      {order.shipping_address?.city || "Не вказано"}
                    </span>
                  </div>
                  <div>
                    Адреса/відділення:{" "}
                    <span className="text-carbon-pitch">
                      {order.shipping_address?.address ||
                        order.shipping_address?.delivery ||
                        "Очікує уточнення"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-gallery-canvas border border-hairline-border space-y-2">
                <div className="flex items-center gap-2 text-carbon-pitch font-bold uppercase tracking-kicker">
                  <Clock className="w-4 h-4 text-carbon-pitch" />
                  <span>ДЕТАЛІ ТРАНЗАКЦІЇ</span>
                </div>
                <div className="text-muted-steel space-y-1">
                  <div>
                    Час фіксації:{" "}
                    <span className="text-carbon-pitch font-bold">
                      {formatDate(order.created_at)}
                    </span>
                  </div>
                  <div>
                    Контакт:{" "}
                    <span className="text-carbon-pitch">
                      {order.buyer_contact}
                    </span>
                  </div>
                  <div>
                    ID платежу:{" "}
                    <span className="text-carbon-pitch font-mono">
                      {order.payment_reference}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-6 bg-pure-white border border-hairline-border flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-electric-blue shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch block">
            РАДИКАЛЬНА ПРИВАТНІСТЬ VEILING
          </span>
          <p className="text-xs text-muted-steel font-sans leading-relaxed">
            Ми не зберігаємо паролів, рекламних профілів та не вимагаємо
            реєстрації для купівлі чи пошуку замовлення. Усі угоди фіксуються
            за криптографічним чек-кодом.
          </p>
        </div>
      </div>
    </div>
  );
};
