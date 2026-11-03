import React, { useState } from "react";
import { Header } from "./components/layout/Header";
import { Footer } from "./components/layout/Footer";
import { Button } from "./components/ui/Button";
import { Badge } from "./components/ui/Badge";
import { SellerStudioPage } from "./pages/seller/SellerStudioPage";
import { HomePage } from "./pages/HomePage";
import { Lot } from "./types";

import { LotDetailPage } from "./pages/LotDetailPage";
import { TakeModal } from "./components/lot/TakeModal";
import { TakeLotResponse } from "./api/lots";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("falling");
  const [selectedLot, setSelectedLot] = useState<Lot | null>(null);
  const [takingLot, setTakingLot] = useState<Lot | null>(null);
  const [claimCodeInput, setClaimCodeInput] = useState<string>("");

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setSelectedLot(null);
  };

  const handleSelectLot = (lot: Lot) => {
    setSelectedLot(lot);
  };

  const handleTakeLot = (lot: Lot) => {
    setTakingLot(lot);
  };

  const handleTakeSuccess = (takeResult: TakeLotResponse, lotId: string) => {
    if (selectedLot && selectedLot.id === lotId) {
      setSelectedLot({
        ...selectedLot,
        status: "TAKEN",
        final_price: takeResult.order.final_price || selectedLot.current_price,
        taken_at: takeResult.order.created_at || new Date().toISOString(),
      });
    }
  };

  return (
    <div className="min-h-screen bg-gallery-canvas text-carbon-pitch flex flex-col font-sans">
      <Header activeTab={activeTab} onTabChange={handleTabChange} />

      <main className="flex-1">
        {selectedLot ? (
          <LotDetailPage
            initialLot={selectedLot}
            onBack={() => setSelectedLot(null)}
            onTake={handleTakeLot}
          />
        ) : (
          <>
            {activeTab === "falling" && (
              <HomePage
                onSelectLot={handleSelectLot}
                onTakeLot={handleTakeLot}
                onNavigateSeller={() => setActiveTab("seller")}
                onNavigateHowItWorks={() => setActiveTab("how-it-works")}
              />
            )}

        {activeTab === "how-it-works" && (
          <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mb-12">
              <span className="text-xs font-mono text-electric-blue font-bold tracking-kicker uppercase block mb-2">
                МЕХАНІКА АУКЦІОНУ
              </span>
              <h2 className="text-3xl font-extrabold tracking-tight">
                Як працює голландський аукціон
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-pure-white border border-hairline-border p-8">
                <div className="text-xs font-mono text-electric-blue font-bold tracking-kicker mb-3">
                  01 / СТЕЛЯ ЦІНИ
                </div>
                <h3 className="text-lg font-bold mb-2">Відкриття на піку</h3>
                <p className="text-xs text-muted-steel leading-relaxed font-sans">
                  Кожен архівний лот відкривається на максимальній оціночній
                  вартості раритету. Це максимальна межа, вище якої ціна ніколи
                  не підніметься.
                </p>
              </div>
              <div className="bg-pure-white border border-hairline-border p-8">
                <div className="text-xs font-mono text-electric-blue font-bold tracking-kicker mb-3">
                  02 / СПУСК ПО ТАЙМЕРУ
                </div>
                <h3 className="text-lg font-bold mb-2">Дискретне падіння</h3>
                <p className="text-xs text-muted-steel leading-relaxed font-sans">
                  Кожні 60 секунд ціна автоматично знижується на фіксований
                  крок. Публічний таймер показує секунди до наступного падіння.
                </p>
              </div>
              <div className="bg-pure-white border border-hairline-border p-8">
                <div className="text-xs font-mono text-electric-blue font-bold tracking-kicker mb-3">
                  03 / ЗАБРАТИ В МОМЕНТ
                </div>
                <h3 className="text-lg font-bold mb-2">Миттєва фіксація</h3>
                <p className="text-xs text-muted-steel leading-relaxed font-sans">
                  Перший покупець, який натисне «Забрати», закріплює експонат
                  за собою за поточною ціною. Аукціон завершується миттєво.
                </p>
              </div>
            </div>
          </section>
        )}

        {activeTab === "ledger" && (
          <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-2xl font-extrabold tracking-tight mb-2">
              Публічний реєстр закритих угод
            </h2>
            <p className="text-xs text-muted-steel font-mono mb-8">
              УСІ ПРЕДМЕТИ Є 1-OF-1 І БІЛЬШЕ НЕ ПОВТОРЮЮТЬСЯ
            </p>
            <div className="bg-pure-white border border-hairline-border overflow-hidden">
              <table className="w-full text-left text-xs font-sans">
                <thead className="bg-gallery-canvas border-b border-hairline-border text-muted-steel font-mono uppercase text-[10px] tracking-kicker">
                  <tr>
                    <th className="p-4">Експонат</th>
                    <th className="p-4">Бренд / Сезон</th>
                    <th className="p-4">Час угоди</th>
                    <th className="p-4 text-right">Фінальна ціна</th>
                    <th className="p-4 text-right">Падіння</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hairline-border">
                  <tr>
                    <td className="p-4 font-bold text-carbon-pitch">
                      Astro Biker Jacket
                    </td>
                    <td className="p-4 text-muted-steel">
                      Helmut Lang · AW99
                    </td>
                    <td className="p-4 font-mono text-muted-steel">
                      24.10.2026 18:02
                    </td>
                    <td className="p-4 font-mono font-bold text-right text-carbon-pitch">
                      132 500 ₴
                    </td>
                    <td className="p-4 text-right">
                      <Badge variant="lime">-26%</Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        )}

        {activeTab === "lookup" && (
          <section className="py-16 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-extrabold tracking-tight mb-3">
              Знайдіть те, що ви забрали
            </h2>
            <p className="text-xs text-muted-steel font-mono mb-6">
              ТУТ НЕМАЄ ОБОВ'ЯЗКОВИХ АКАУНТІВ. ВВЕДІТЬ ВАШ ЧЕК-КОД.
            </p>
            <div className="bg-pure-white border border-hairline-border p-6 space-y-4">
              <div>
                <label className="block text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch mb-2">
                  КОД КВИТАНЦІЇ ЗАКРІПЛЕННЯ
                </label>
                <input
                  type="text"
                  placeholder="V-2026-XXXX-XXXX-XXXX"
                  value={claimCodeInput}
                  onChange={(e) => setClaimCodeInput(e.target.value)}
                  className="w-full border border-hairline-border px-4 py-3 font-mono text-sm uppercase tracking-wider focus:outline-none focus:border-carbon-pitch rounded-none"
                />
              </div>
              <Button variant="primary" size="lg" className="w-full">
                ПОШУК КВИТАНЦІЇ
              </Button>
            </div>
          </section>
        )}

        {activeTab === "seller" && (
          <SellerStudioPage
            onNavigateHome={() => handleTabChange("falling")}
            onLotCreated={() => handleTabChange("falling")}
          />
        )}

        {activeTab !== "seller" && activeTab !== "falling" && (
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
                  VEILING забезпечує прямий доступ до колекціонерів світового рівня
                  без затяжних торгів.
                </p>
              </div>
              <Button
                variant="accent"
                size="lg"
                onClick={() => setActiveTab("seller")}
              >
                СТВОРИТИ ЛОТ
              </Button>
            </div>
          </section>
        )}
      </>
    )}
      </main>

      <TakeModal
        lot={takingLot}
        isOpen={Boolean(takingLot)}
        onClose={() => setTakingLot(null)}
        onSuccess={handleTakeSuccess}
      />

      <Footer />
    </div>
  );
};
