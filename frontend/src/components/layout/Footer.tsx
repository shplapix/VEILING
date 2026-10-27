import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-carbon-pitch text-pure-white border-t border-hairline-border/20 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <div className="flex items-center text-lg font-extrabold tracking-wordmark uppercase">
              VEILING
              <span className="inline-block w-3 h-3 bg-acid-lime ml-1.5" />
            </div>
            <p className="text-xs text-muted-steel leading-relaxed font-sans">
              Дім голландського аукціону культового та музейного архівного одягу.
              Амстердам — Київ.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-mono font-bold tracking-kicker uppercase text-muted-steel mb-3">
              НАВІГАЦІЯ
            </h4>
            <ul className="space-y-2 text-xs font-sans text-muted-steel">
              <li>
                <a href="#falling" className="hover:text-pure-white transition-colors">
                  Падає зараз
                </a>
              </li>
              <li>
                <a href="#how" className="hover:text-pure-white transition-colors">
                  Механіка голландського аукціону
                </a>
              </li>
              <li>
                <a href="#ledger" className="hover:text-pure-white transition-colors">
                  Публічний реєстр угод
                </a>
              </li>
              <li>
                <a href="#lookup" className="hover:text-pure-white transition-colors">
                  Пошук за квитанцією
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-mono font-bold tracking-kicker uppercase text-muted-steel mb-3">
              КУЛЬТОВІ АРХІВИ
            </h4>
            <ul className="space-y-2 text-xs font-sans text-muted-steel">
              <li>Raf Simons (1997–2003)</li>
              <li>Helmut Lang (1997–2004)</li>
              <li>Maison Martin Margiela (1989–2009)</li>
              <li>Undercover (1996–2004)</li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-mono font-bold tracking-kicker uppercase text-muted-steel mb-3">
              МАНІФЕСТ
            </h4>
            <p className="text-xs text-muted-steel leading-relaxed font-mono">
              The price only goes down. You are never outbid — you are only ever
              early or late.
            </p>
          </div>
        </div>

        <div className="mt-12 pt-6 border-t border-hairline-border/10 flex flex-col sm:flex-row items-center justify-between text-xs text-muted-steel font-mono">
          <div>© 2026 VEILING ■ ARCHIVE AUCTION HOUSE</div>
          <div className="mt-2 sm:mt-0">ZERO-ACCOUNT CLAIM RECEIPT MODEL</div>
        </div>
      </div>
    </footer>
  );
};
