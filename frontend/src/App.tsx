import React, { useState } from "react";
import { Header } from "./components/layout/Header";
import { Footer } from "./components/layout/Footer";
import { Button } from "./components/ui/Button";
import { Badge } from "./components/ui/Badge";
import { ArrowDownRight, Clock, ShieldCheck, TrendingDown } from "lucide-react";
import { SellerStudioPage } from "./pages/seller/SellerStudioPage";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("falling");
  const [claimCodeInput, setClaimCodeInput] = useState<string>("");

  return (
    <div className="min-h-screen bg-gallery-canvas text-carbon-pitch flex flex-col font-sans">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="flex-1">
        {activeTab === "falling" && (
          <section className="border-b border-hairline-border bg-pure-white py-16 sm:py-24">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="max-w-3xl">
                <div className="inline-flex items-center space-x-2 text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch mb-4">
                  <span className="w-2.5 h-2.5 bg-acid-lime inline-block" />
                  <span>ГОЛЛАНДСЬКИЙ АУКЦІОН · ЦІНА ПАДАЄ НА ТАЙМЕРІ</span>
                </div>
                <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-hero leading-[1.05] mb-6">
                  The price only goes{" "}
                  <span className="text-electric-blue">down.</span>
                </h1>
                <p className="text-base sm:text-lg text-muted-steel leading-relaxed font-sans mb-8">
                  Зворотний відлік, за яким ви спостерігаєте, а не аукціон, який
                  ви можете програти. У кожен момент є лише одна ціна, і вона
                  належить тому, хто забере її першим.
                </p>
                <div className="flex flex-wrap items-center gap-4">
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={() => setActiveTab("falling")}
                  >
                    ДИВИТИСЯ ЩО ПАДАЄ ЗАРАЗ
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => setActiveTab("how-it-works")}
                  >
                    ЯК ПРАЦЮЄ СПУСК
                  </Button>
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === "falling" && (
          <section className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
                  Падає прямо зараз
                </h2>
                <p className="text-xs text-muted-steel font-mono mt-1">
                  1 АКТИВНИЙ АУКЦІОН У РЕАЛЬНОМУ ЧАСІ
                </p>
              </div>
              <Badge variant="blue">LIVE ТРАНСЛЯЦІЯ</Badge>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 bg-pure-white border border-hairline-border p-6 flex flex-col md:flex-row gap-6">
                <div className="w-full md:w-1/2 aspect-square bg-gallery-canvas border border-hairline-border flex items-center justify-center relative overflow-hidden">
                  <div className="text-center p-6 select-none">
                    <span className="text-xs font-mono text-muted-steel uppercase tracking-kicker block mb-2">
                      RAF SIMONS AW01
                    </span>
                    <span className="text-xl font-extrabold tracking-tight">
                      "Riot! Riot! Riot!" Camo Bomber
                    </span>
                    <span className="text-xs text-muted-steel font-mono block mt-2">
                      Розмір 50 · Музейний стан 9/10
                    </span>
                  </div>
                  <div className="absolute top-3 left-3">
                    <Badge variant="lime">АКТИВНИЙ СПУСК</Badge>
                  </div>
                </div>

                <div className="w-full md:w-1/2 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-xs text-muted-steel font-mono mb-2">
                      <span>ПОТОЧНА ЦІНА</span>
                      <span className="flex items-center text-electric-blue">
                        <Clock className="w-3.5 h-3.5 mr-1" />
                        НАСТУПНИЙ КРОК ЧЕРЕЗ 00:42
                      </span>
                    </div>
                    <div className="text-4xl sm:text-5xl font-extrabold font-mono tracking-tight text-carbon-pitch mb-2">
                      145 000 ₴
                    </div>
                    <div className="text-xs text-muted-steel font-mono flex items-center space-x-3 mb-6">
                      <span className="line-through">Стеля: 180 000 ₴</span>
                      <span className="text-electric-blue font-bold">
                        Економія: -19%
                      </span>
                    </div>

                    <div className="space-y-2 mb-6">
                      <div className="flex justify-between text-[11px] font-mono text-muted-steel">
                        <span>Стеля: 180 000 ₴</span>
                        <span>Підлога: 90 000 ₴</span>
                      </div>
                      <div className="w-full h-2 bg-gallery-canvas border border-hairline-border overflow-hidden">
                        <div
                          className="h-full bg-electric-blue"
                          style={{ width: "38%" }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Button
                      variant="primary"
                      size="lg"
                      className="w-full flex items-center justify-center space-x-2"
                    >
                      <ArrowDownRight className="w-4 h-4" />
                      <span>ЗАБРАТИ ЗА 145 000 ₴</span>
                    </Button>
                    <p className="text-[11px] text-muted-steel text-center font-mono">
                      Атомарна фіксація. Перший клік закріплює річ назавжди.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-pure-white border border-hairline-border p-6 flex flex-col justify-between">
                <div>
                  <h3 className="text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch mb-4">
                    МЕХАНІКА АУКЦІОНУ
                  </h3>
                  <div className="space-y-4 text-xs font-sans text-muted-steel">
                    <div className="flex items-start space-x-3">
                      <TrendingDown className="w-4 h-4 text-carbon-pitch flex-shrink-0 mt-0.5" />
                      <p>
                        Ціна крокує вниз на 2 500 ₴ кожні 60 секунд до
                        досягнення підлоги ціни 90 000 ₴.
                      </p>
                    </div>
                    <div className="flex items-start space-x-3">
                      <ShieldCheck className="w-4 h-4 text-carbon-pitch flex-shrink-0 mt-0.5" />
                      <p>
                        Безаккаунтна покупка. Миттєва генерація коду квитанції
                        формату V-2026-XXXX-XXXX.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="border-t border-hairline-border pt-4 mt-6">
                  <div className="text-[11px] font-mono text-muted-steel uppercase tracking-kicker">
                    ПРОХОДЖЕННЯ
                  </div>
                  <div className="text-xs text-carbon-pitch font-sans mt-1">
                    Автентичність підтверджена архівом Амстердама. Повний комплект
                    первинних бірок.
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === "how-it-works" && (
          <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-extrabold tracking-tight mb-8">
              Як працює голландський аукціон
            </h2>
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
            onNavigateHome={() => setActiveTab("falling")}
            onLotCreated={() => setActiveTab("falling")}
          />
        )}

        {activeTab !== "seller" && (
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
      </main>

      <Footer />
    </div>
  );
};
