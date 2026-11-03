import React, { useState } from "react";
import { Lot } from "../../types";
import { ChevronDown, ChevronUp, Ruler, ShieldAlert, Sparkles, Truck } from "lucide-react";

interface SpecsAccordionProps {
  lot: Lot;
}

export const SpecsAccordion: React.FC<SpecsAccordionProps> = ({ lot }) => {
  const [openSection, setOpenSection] = useState<string>("measurements");

  const toggleSection = (id: string) => {
    setOpenSection((prev) => (prev === id ? "" : id));
  };

  const measurementsEntries = Object.entries(lot.measurements || {}).filter(
    ([, val]) => val !== undefined && val !== null && val > 0
  );

  const measurementLabels: Record<string, string> = {
    pit_to_pit: "Ширина під пахвами (Pit to pit)",
    length: "Довжина по спині (Length)",
    shoulders: "Ширина в плечах (Shoulders)",
    sleeve: "Довжина рукава (Sleeve)",
    waist: "Напівобхват талії (Waist)",
    inseam: "Внутрішній шов (Inseam)",
    hem: "Ширина низу (Hem)",
  };

  return (
    <div className="border border-hairline-border bg-pure-white divide-y divide-hairline-border">
      <div>
        <button
          type="button"
          onClick={() => toggleSection("measurements")}
          className="w-full p-4 flex items-center justify-between text-left text-xs font-mono font-bold uppercase tracking-kicker hover:bg-gallery-canvas/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            <Ruler className="w-4 h-4 text-carbon-pitch" />
            <span>ТОЧНІ ЗАМІРИ В САНТИМЕТРАХ</span>
          </span>
          {openSection === "measurements" ? (
            <ChevronUp className="w-4 h-4 text-muted-steel" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-steel" />
          )}
        </button>
        {openSection === "measurements" && (
          <div className="p-4 pt-0 text-xs font-mono">
            {measurementsEntries.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-hairline-border">
                {measurementsEntries.map(([key, val]) => (
                  <div
                    key={key}
                    className="flex justify-between py-1 border-b border-hairline-border/60"
                  >
                    <span className="text-muted-steel">
                      {measurementLabels[key] || key}:
                    </span>
                    <span className="font-bold text-carbon-pitch">
                      {val} см
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-steel pt-2">
                Розмір на бірці: {lot.tagged_size}. Посадка: {lot.fits_like}.
              </p>
            )}
          </div>
        )}
      </div>

      <div>
        <button
          type="button"
          onClick={() => toggleSection("materials")}
          className="w-full p-4 flex items-center justify-between text-left text-xs font-mono font-bold uppercase tracking-kicker hover:bg-gallery-canvas/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-carbon-pitch" />
            <span>СКЛАД ТА МАТЕРІАЛИ</span>
          </span>
          {openSection === "materials" ? (
            <ChevronUp className="w-4 h-4 text-muted-steel" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-steel" />
          )}
        </button>
        {openSection === "materials" && (
          <div className="p-4 pt-0 text-xs space-y-2 pt-2 border-t border-hairline-border font-sans">
            <div>
              <span className="font-mono text-muted-steel text-[11px] uppercase block">
                ОСНОВНА ТКАНИНА (OUTER):
              </span>
              <span className="text-carbon-pitch font-medium">
                {lot.materials?.outer || "Не вказано"}
              </span>
            </div>
            {lot.materials?.lining && (
              <div>
                <span className="font-mono text-muted-steel text-[11px] uppercase block">
                  ПІДКЛАДКА (LINING):
                </span>
                <span className="text-carbon-pitch font-medium">
                  {lot.materials.lining}
                </span>
              </div>
            )}
            {lot.materials?.hardware && (
              <div>
                <span className="font-mono text-muted-steel text-[11px] uppercase block">
                  ФУРНІТУРА (HARDWARE):
                </span>
                <span className="text-carbon-pitch font-medium">
                  {lot.materials.hardware}
                </span>
              </div>
            )}
            <div>
              <span className="font-mono text-muted-steel text-[11px] uppercase block">
                КРАЇНА ВИРОБНИЦТВА:
              </span>
              <span className="text-carbon-pitch font-medium">
                {lot.country_of_origin}
              </span>
            </div>
          </div>
        )}
      </div>

      <div>
        <button
          type="button"
          onClick={() => toggleSection("condition")}
          className="w-full p-4 flex items-center justify-between text-left text-xs font-mono font-bold uppercase tracking-kicker hover:bg-gallery-canvas/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-carbon-pitch" />
            <span>ОЦІНКА СТАНУ ({lot.condition_rating}/10) ТА ПАТИНА</span>
          </span>
          {openSection === "condition" ? (
            <ChevronUp className="w-4 h-4 text-muted-steel" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-steel" />
          )}
        </button>
        {openSection === "condition" && (
          <div className="p-4 pt-0 text-xs space-y-2 pt-2 border-t border-hairline-border font-sans">
            <p className="text-carbon-pitch leading-relaxed">
              {lot.condition_details}
            </p>
            {lot.provenance_notes && (
              <div className="pt-2 border-t border-hairline-border/60">
                <span className="font-mono text-[11px] text-muted-steel uppercase block mb-1">
                  ПРОВЕНАНС ЕКСПОНАТУ:
                </span>
                <p className="text-muted-steel leading-relaxed">
                  {lot.provenance_notes}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      <div>
        <button
          type="button"
          onClick={() => toggleSection("shipping")}
          className="w-full p-4 flex items-center justify-between text-left text-xs font-mono font-bold uppercase tracking-kicker hover:bg-gallery-canvas/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            <Truck className="w-4 h-4 text-carbon-pitch" />
            <span>ДОСТАВКА ТА ЛОКАЦІЯ ВІДПРАВКИ</span>
          </span>
          {openSection === "shipping" ? (
            <ChevronUp className="w-4 h-4 text-muted-steel" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-steel" />
          )}
        </button>
        {openSection === "shipping" && (
          <div className="p-4 pt-0 text-xs space-y-2 pt-2 border-t border-hairline-border font-sans">
            <div className="font-mono text-[11px] text-muted-steel uppercase">
              МІСТО ВІДПРАВКИ:{" "}
              <span className="text-carbon-pitch font-bold">
                {lot.seller_location}
              </span>
            </div>
            <p className="text-carbon-pitch leading-relaxed">
              {lot.shipping_notes}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
