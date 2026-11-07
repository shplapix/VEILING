import React, { useEffect, useState } from "react";
import { Lot } from "../../types";
import { takeLot, TakeLotResponse } from "../../api/lots";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  Copy,
  ShieldCheck,
  X,
} from "lucide-react";

interface TakeModalProps {
  lot: Lot | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (takeResult: TakeLotResponse, lotId: string) => void;
  onLotConflict?: (lotId: string) => void;
}

export const TakeModal: React.FC<TakeModalProps> = ({
  lot,
  isOpen,
  onClose,
  onSuccess,
  onLotConflict,
}) => {
  const [buyerContact, setBuyerContact] = useState<string>("");
  const [recipientName, setRecipientName] = useState<string>("");
  const [city, setCity] = useState<string>("");
  const [deliveryAddress, setDeliveryAddress] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [conflictError, setConflictError] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<TakeLotResponse | null>(null);
  const [isCopied, setIsCopied] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen && lot) {
      setErrorMessage(null);
      setConflictError(null);
      setSuccessData(null);
      setIsLoading(false);
      setIsCopied(false);
    }
  }, [isOpen, lot?.id]);

  useEffect(() => {
    if (isOpen && lot && !successData && !isLoading) {
      if (lot.status === "TAKEN") {
        setConflictError("Цю річ щойно забрав інший покупець");
      } else if (lot.status === "EXPIRED") {
        setConflictError("Час спуску лота вичерпано. Досягнуто мінімальної ціни.");
      } else if (lot.status === "CANCELLED") {
        setConflictError("Аукціон для цього експонату було скасовано.");
      }
    }
  }, [isOpen, lot?.status, successData, isLoading]);

  if (!isOpen || !lot) {
    return null;
  }

  const formatNumber = (num: number): string => {
    return Math.round(num)
      .toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  const handleCopyCode = async () => {
    if (!successData?.claim_code) {
      return;
    }
    try {
      await navigator.clipboard.writeText(successData.claim_code);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch {
      return;
    }
  };

  const handleExecuteTake = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lot || isLoading) {
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    setConflictError(null);

    try {
      const response = await takeLot(lot.id, {
        buyer_contact: buyerContact.trim() || "collector@veiling.archive",
        shipping_address: {
          recipient_name: recipientName.trim() || "Анонімний покупець",
          city: city.trim() || "Київ",
          address: deliveryAddress.trim() || "Кур'єрська доставка",
          country: "Україна",
        },
      });

      setSuccessData(response);
      onSuccess(response, lot.id);
    } catch (err: unknown) {
      const status =
        typeof err === "object" && err !== null && "response" in err
          ? (err as { response?: { status?: number; data?: { detail?: unknown } } })
              .response?.status
          : null;

      const rawDetail =
        typeof err === "object" && err !== null && "response" in err
          ? (err as { response?: { data?: { detail?: unknown } } }).response?.data
              ?.detail
          : null;

      let detailString: string | null = null;
      if (typeof rawDetail === "string") {
        detailString = rawDetail;
      } else if (Array.isArray(rawDetail) && rawDetail.length > 0) {
        detailString = rawDetail
          .map((item: { msg?: string }) => item?.msg || String(item))
          .join(", ");
      }

      if (status === 409) {
        setConflictError(detailString || "Цю річ уже забрав інший покупець");
        onLotConflict?.(lot.id);
      } else {
        setErrorMessage(
          detailString || "Помилка при взятті лота. Будь ласка, спробуйте ще раз."
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-carbon-pitch/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-lg bg-pure-white border border-hairline-border shadow-2xl overflow-hidden rounded-none">
        <div className="flex items-center justify-between p-6 border-b border-hairline-border bg-gallery-canvas">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-acid-lime inline-block" />
            <span className="text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch">
              {successData
                ? "КВИТАНЦІЯ ЗАКРІПЛЕННЯ УГОДИ"
                : conflictError
                ? "УВАГА: СТАТУС ЛОТА ЗМІНЕНО"
                : "АТОМАРНЕ ВЗЯТТЯ ЛОТА"}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-muted-steel hover:text-carbon-pitch transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {successData ? (
          <div className="p-6 sm:p-8 space-y-6">
            <div className="space-y-2">
              <Badge variant="lime">УСПІШНО ЗАБРАНО</Badge>
              <h3 className="text-2xl font-extrabold text-carbon-pitch tracking-tight">
                {lot.title}
              </h3>
              <p className="text-xs text-muted-steel font-mono">
                {lot.brand} · {lot.season} {lot.year} · Розмір {lot.tagged_size}
              </p>
            </div>

            <div className="p-5 bg-gallery-canvas border border-hairline-border space-y-4">
              <div>
                <span className="text-[11px] font-mono text-muted-steel uppercase tracking-kicker block mb-1">
                  ВАШ УНІКАЛЬНИЙ ЧЕК-КОД (CLAIM CODE)
                </span>
                <div className="flex items-center justify-between gap-2 p-3 bg-pure-white border border-carbon-pitch font-mono text-base sm:text-lg font-bold text-carbon-pitch tracking-wider select-all">
                  <span>{successData.claim_code}</span>
                  <button
                    type="button"
                    onClick={handleCopyCode}
                    className="p-1.5 hover:bg-gallery-canvas text-carbon-pitch transition-colors shrink-0"
                    title="Копіювати код"
                  >
                    {isCopied ? (
                      <Check className="w-5 h-5 text-emerald-600" />
                    ) : (
                      <Copy className="w-5 h-5 text-carbon-pitch" />
                    )}
                  </button>
                </div>
                {isCopied && (
                  <span className="text-[10px] font-mono text-emerald-600 font-bold tracking-wider mt-1 block">
                    КОД СКОПІЙОВАНО В БУФЕР ОБМІНУ ■
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-hairline-border text-xs font-mono">
                <div>
                  <span className="text-muted-steel text-[10px] uppercase block">
                    ФІКСОВАНА ЦІНА
                  </span>
                  <span className="text-base font-bold text-carbon-pitch">
                    {formatNumber(successData.order.final_price)} ₴
                  </span>
                </div>
                <div>
                  <span className="text-muted-steel text-[10px] uppercase block">
                    ЕКОНОМІЯ ВІД СТЕЛІ
                  </span>
                  <span className="text-base font-bold text-electric-blue">
                    -{successData.order.savings_percentage}%
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-start gap-2.5 text-xs font-sans text-carbon-pitch bg-pure-white p-3 border border-hairline-border">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>
                  Збережіть цей чек-код. Тут немає обов'язкових акаунтів — код є
                  єдиним ключем для відстеження статусу замовлення в розділі
                  «Пошук квитанції».
                </span>
              </div>

              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={onClose}
              >
                ПОВЕРНУТИСЯ ДО КАТАЛОГУ
              </Button>
            </div>
          </div>
        ) : conflictError ? (
          <div className="p-6 sm:p-8 space-y-6">
            <div className="p-4 bg-gallery-canvas border border-hairline-border space-y-2">
              <div className="flex items-center gap-2 text-carbon-pitch font-bold text-sm">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                <span>{conflictError}</span>
              </div>
              <p className="text-xs text-muted-steel leading-relaxed font-sans">
                У голландському аукціоні VEILING кожен експонат існує в єдиному
                екземплярі. Інший покупець встиг зафіксувати транзакцію на мить
                раніше.
              </p>
            </div>

            <Button
              variant="outline"
              size="lg"
              className="w-full"
              onClick={onClose}
            >
              ЗАКРИТИ ТА ПОВЕРНУТИСЯ ДО КАТАЛОГУ
            </Button>
          </div>
        ) : (
          <form onSubmit={handleExecuteTake} className="p-6 sm:p-8 space-y-6">
            <div className="space-y-2">
              <span className="text-xs font-mono text-muted-steel uppercase tracking-kicker">
                ПІДТВЕРДЖЕННЯ ЗАКРІПЛЕННЯ ЕКСПОНАТУ
              </span>
              <h3 className="text-xl sm:text-2xl font-extrabold text-carbon-pitch tracking-tight">
                {lot.title}
              </h3>
              <div className="flex items-baseline gap-3 pt-1">
                <span className="text-3xl font-extrabold font-mono text-carbon-pitch tabular-nums">
                  {formatNumber(lot.current_price)} ₴
                </span>
                <span className="text-xs font-mono text-muted-steel line-through tabular-nums">
                  Стеля: {formatNumber(lot.start_price)} ₴
                </span>
              </div>
            </div>

            {errorMessage && (
              <div className="p-3 bg-red-50 border border-red-200 text-xs font-mono text-red-700 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="space-y-4 pt-2 border-t border-hairline-border">
              <div>
                <label className="block text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch mb-1.5">
                  КОНТАКТ ДЛЯ ПІДТВЕРДЖЕННЯ (EMAIL АБО ТЕЛЕФОН)
                </label>
                <input
                  type="text"
                  placeholder="collector@archive.ua"
                  value={buyerContact}
                  onChange={(e) => setBuyerContact(e.target.value)}
                  className="w-full border border-hairline-border px-4 py-2.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none"
                />
              </div>

              <div>
                <label className="block text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch mb-1.5">
                  ПІБ ОДЕРЖУВАЧА
                </label>
                <input
                  type="text"
                  placeholder="Іван Ковальчук"
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                  className="w-full border border-hairline-border px-4 py-2.5 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch mb-1.5">
                    МІСТО ДОСТАВКИ
                  </label>
                  <input
                    type="text"
                    placeholder="Київ"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full border border-hairline-border px-4 py-2.5 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch mb-1.5">
                    ВІДДІЛЕННЯ / АДРЕСА
                  </label>
                  <input
                    type="text"
                    placeholder="Відділення №1"
                    value={deliveryAddress}
                    onChange={(e) => setDeliveryAddress(e.target.value)}
                    className="w-full border border-hairline-border px-4 py-2.5 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <Button
                variant="primary"
                size="lg"
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center space-x-2 py-4"
              >
                <span>
                  {isLoading
                    ? "ФІКСАЦІЯ ТРАНЗАКЦІЇ..."
                    : `ЗАБРАТИ ЗА ${formatNumber(lot.current_price)} ₴`}
                </span>
                <ArrowRight className="w-4 h-4" />
              </Button>

              <div className="flex items-center justify-center gap-1.5 text-[11px] font-mono text-muted-steel text-center">
                <ShieldCheck className="w-3.5 h-3.5 text-carbon-pitch" />
                <span>МИТТЄВА БЕЗАККАУНТНА ФІКСАЦІЯ В РЕЄСТРІ</span>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
