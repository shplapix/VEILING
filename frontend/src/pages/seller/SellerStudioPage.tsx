import React, { useState, useId } from "react";
import {
  Upload,
  X,
  AlertCircle,
  ShieldCheck,
  Eye,
} from "lucide-react";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { createLot, uploadLotImage } from "../../api/lots";
import { login, register, getStoredToken } from "../../api/auth";
import {
  Lot,
  LotCategory,
  LotCreatePayload,
  LotImageCreatePayload,
  LotStatus,
} from "../../types";

interface SellerStudioPageProps {
  onLotCreated?: (lot: Lot) => void;
  onNavigateHome?: () => void;
}

interface UploadedPhoto {
  id: string;
  url: string;
  file?: File;
  caption: string;
}

export const SellerStudioPage: React.FC<SellerStudioPageProps> = ({
  onLotCreated,
  onNavigateHome,
}) => {
  const photoInputId = useId();
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [authEmail, setAuthEmail] = useState<string>("seller@veiling.test");
  const [authPassword, setAuthPassword] = useState<string>("SecureSeller2026!");
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState<boolean>(false);

  const [title, setTitle] = useState<string>(
    'Бомбер Raf Simons AW01 "Riot! Riot! Riot!"'
  );
  const [brand, setBrand] = useState<string>("Raf Simons");
  const [designer, setDesigner] = useState<string>("Raf Simons");
  const [season, setSeason] = useState<string>("Autumn/Winter");
  const [year, setYear] = useState<number>(2001);
  const [collectionName, setCollectionName] = useState<string>(
    '"Riot! Riot! Riot!"'
  );
  const [category, setCategory] = useState<LotCategory>("OUTERWEAR");
  const [subcategory, setSubcategory] = useState<string>(
    "Бомбер / Camo Bomber"
  );
  const [taggedSize, setTaggedSize] = useState<string>("50");
  const [fitsLike, setFitsLike] = useState<string>("Oversized L");

  const [pitToPit, setPitToPit] = useState<number>(62);
  const [length, setLength] = useState<number>(71);
  const [shoulders, setShoulders] = useState<number>(54);
  const [sleeve, setSleeve] = useState<number>(66);
  const [waist, setWaist] = useState<number>(0);
  const [inseam, setInseam] = useState<number>(0);
  const [hem, setHem] = useState<number>(58);

  const [outerMaterial, setOuterMaterial] = useState<string>(
    "100% Cotton Camo Gabardine"
  );
  const [liningMaterial, setLiningMaterial] = useState<string>("100% Cupro");
  const [hardwareMaterial, setHardwareMaterial] = useState<string>(
    "Блискавки Raccagni"
  );

  const [conditionRating, setConditionRating] = useState<number>(9);
  const [conditionDetails, setConditionDetails] = useState<string>(
    "Музейне архівне збереження, природна вінтажна патина бавовни, оригінальні патчі з туру Manic Street Preachers."
  );
  const [countryOfOrigin, setCountryOfOrigin] = useState<string>(
    "Зроблено в Бельгії"
  );
  const [provenanceNotes, setProvenanceNotes] = useState<string>(
    "Приватна архівна колекція, придбано на показі в Парижі 2001 року."
  );
  const [sellerLocation, setSellerLocation] = useState<string>(
    "Амстердам, Нідерланди"
  );
  const [shippingNotes, setShippingNotes] = useState<string>(
    "Застрахована кур'єрська доставка по Європі та Україні (3–5 робочих днів)"
  );

  const [startPrice, setStartPrice] = useState<number>(180000);
  const [floorPrice, setFloorPrice] = useState<number>(90000);
  const [stepAmount, setStepAmount] = useState<number>(2500);
  const [intervalSeconds, setIntervalSeconds] = useState<number>(60);
  const [lotStatus] = useState<LotStatus>("ACTIVE");

  const [photos, setPhotos] = useState<UploadedPhoto[]>([
    {
      id: "demo-1",
      url: "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=1000&q=80",
      caption: "Головний силует експонату",
    },
  ]);
  const [isUploadingPhoto, setIsUploadingPhoto] = useState<boolean>(false);
  const [photoError, setPhotoError] = useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [createdLot, setCreatedLot] = useState<Lot | null>(null);

  const totalDrop = Math.max(0, startPrice - floorPrice);
  const totalSteps = stepAmount > 0 ? Math.ceil(totalDrop / stepAmount) : 0;
  const totalDurationSeconds = totalSteps * intervalSeconds;
  const totalHours = Math.floor(totalDurationSeconds / 3600);
  const remainingMinutes = Math.floor((totalDurationSeconds % 3600) / 60);
  const maxSavingsPct =
    startPrice > 0
      ? Math.round(((startPrice - floorPrice) / startPrice) * 100)
      : 0;

  const scheduleRows = [];
  const maxDisplaySteps = Math.min(8, totalSteps);
  for (let i = 0; i <= maxDisplaySteps; i++) {
    const stepPrice = Math.max(floorPrice, startPrice - i * stepAmount);
    const stepTimeSeconds = i * intervalSeconds;
    const m = Math.floor(stepTimeSeconds / 60);
    const s = stepTimeSeconds % 60;
    const timeFormatted = `${m < 10 ? `0${m}` : m}:${s < 10 ? `0${s}` : s}`;
    const savings =
      startPrice > 0
        ? Math.round(((startPrice - stepPrice) / startPrice) * 100)
        : 0;
    scheduleRows.push({
      step: i,
      time: timeFormatted,
      price: stepPrice,
      savings,
    });
    if (stepPrice <= floorPrice) break;
  }

  const handleQuickSellerLogin = async () => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      try {
        const resp = await login(authEmail, authPassword);
        setToken(resp.access_token);
      } catch {
        const resp = await register(
          authEmail,
          authPassword,
          "Архівний Продавець",
          "SELLER"
        );
        setToken(resp.access_token);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Помилка автентифікації";
      setAuthError(msg);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setPhotoError(null);
    setIsUploadingPhoto(true);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (token) {
          try {
            const uploadRes = await uploadLotImage(file);
            setPhotos((prev) => [
              ...prev,
              {
                id: uploadRes.key,
                url: uploadRes.image_url,
                caption: `Ракурс ${prev.length + 1}`,
              },
            ]);
          } catch {
            const localUrl = URL.createObjectURL(file);
            setPhotos((prev) => [
              ...prev,
              {
                id: `local-${Date.now()}-${i}`,
                url: localUrl,
                file,
                caption: `Ракурс ${prev.length + 1}`,
              },
            ]);
          }
        } else {
          const localUrl = URL.createObjectURL(file);
          setPhotos((prev) => [
            ...prev,
            {
              id: `local-${Date.now()}-${i}`,
              url: localUrl,
              file,
              caption: `Ракурс ${prev.length + 1}`,
            },
          ]);
        }
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Не вдалося завантажити фото";
      setPhotoError(msg);
    } finally {
      setIsUploadingPhoto(false);
      e.target.value = "";
    }
  };

  const handleRemovePhoto = (id: string) => {
    setPhotos((prev) => prev.filter((p) => p.id !== id));
  };

  const handleCaptionChange = (id: string, newCaption: string) => {
    setPhotos((prev) =>
      prev.map((p) => (p.id === id ? { ...p, caption: newCaption } : p))
    );
  };

  const handleSubmitLot = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    if (!token) {
      setSubmitError(
        "Будь ласка, увійдіть як продавець перед створенням лота."
      );
      return;
    }

    if (!title.trim() || !brand.trim()) {
      setSubmitError("Назва та бренд є обов'язковими полями.");
      return;
    }

    if (startPrice < floorPrice) {
      setSubmitError("Стеля ціни повинна бути більшою або рівною за підлогу.");
      return;
    }

    if (startPrice <= 0 || floorPrice <= 0 || stepAmount <= 0) {
      setSubmitError("Цінові параметри повинні бути більшими за 0.");
      return;
    }

    setIsSubmitting(true);

    try {
      const lotImages: LotImageCreatePayload[] = photos.map((p, idx) => ({
        image_url: p.url,
        sort_order: idx,
        display_order: idx,
        caption: p.caption,
      }));

      const payload: LotCreatePayload = {
        title: title.trim(),
        brand: brand.trim(),
        designer: designer.trim() || brand.trim(),
        season: season.trim(),
        year: Number(year),
        collection_name: collectionName.trim() || null,
        category,
        subcategory: subcategory.trim(),
        tagged_size: taggedSize.trim(),
        fits_like: fitsLike.trim(),
        measurements: {
          pit_to_pit: pitToPit > 0 ? pitToPit : undefined,
          length: length > 0 ? length : undefined,
          shoulders: shoulders > 0 ? shoulders : undefined,
          sleeve: sleeve > 0 ? sleeve : undefined,
          waist: waist > 0 ? waist : undefined,
          inseam: inseam > 0 ? inseam : undefined,
          hem: hem > 0 ? hem : undefined,
        },
        materials: {
          outer: outerMaterial.trim(),
          lining: liningMaterial.trim() || undefined,
          hardware: hardwareMaterial.trim() || undefined,
        },
        condition_rating: Number(conditionRating),
        condition_details: conditionDetails.trim(),
        country_of_origin: countryOfOrigin.trim(),
        provenance_notes: provenanceNotes.trim() || null,
        seller_location: sellerLocation.trim(),
        shipping_notes: shippingNotes.trim(),
        start_price: Number(startPrice),
        floor_price: Number(floorPrice),
        step_amount: Number(stepAmount),
        interval_seconds: Number(intervalSeconds),
        status: lotStatus,
        images: lotImages,
      };

      const result = await createLot(payload);
      setCreatedLot(result);
      onLotCreated?.(result);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Не вдалося створити лот";
      setSubmitError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (createdLot) {
    return (
      <div className="py-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-pure-white border-2 border-carbon-pitch p-8 sm:p-12 space-y-6">
          <div className="inline-flex items-center space-x-2 text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch">
            <span className="w-2.5 h-2.5 bg-acid-lime inline-block" />
            <span>ЛОТ УСПІШНО ОПУБЛІКОВАНО · АУКЦІОН СТАРТУВАВ</span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            {createdLot.title}
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-gallery-canvas border border-hairline-border font-mono text-xs">
            <div>
              <span className="text-muted-steel block">СТЕЛЯ ЦІНИ</span>
              <span className="font-bold text-sm">
                {Number(createdLot.start_price).toLocaleString()} ₴
              </span>
            </div>
            <div>
              <span className="text-muted-steel block">ПІДЛОГА ЗУПИНКИ</span>
              <span className="font-bold text-sm">
                {Number(createdLot.floor_price).toLocaleString()} ₴
              </span>
            </div>
            <div>
              <span className="text-muted-steel block">КРОК ПАДІННЯ</span>
              <span className="font-bold text-sm">
                -{Number(createdLot.step_amount).toLocaleString()} ₴
              </span>
            </div>
            <div>
              <span className="text-muted-steel block">ІНТЕРВАЛ</span>
              <span className="font-bold text-sm">
                {createdLot.interval_seconds} сек
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 pt-4">
            <Button
              variant="primary"
              size="lg"
              onClick={() => {
                setCreatedLot(null);
                onNavigateHome?.();
              }}
            >
              ПЕРЕЙТИ В КАТАЛОГ ПАДАЮЧИХ ЛОТІВ
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => {
                setCreatedLot(null);
              }}
            >
              СТВОРИТИ ЩЕ ОДИН ЛОТ
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-8 border-b border-hairline-border pb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 text-xs font-mono font-bold tracking-kicker uppercase text-carbon-pitch mb-2">
            <span className="w-2.5 h-2.5 bg-acid-lime inline-block" />
            <span>СТУДІЯ ПРОДАВЦЯ · РОЗДІЛ ДЛЯ ВЛАСНИКІВ АРХІВУ</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight">
            Створення архівного лота
          </h1>
          <p className="text-sm text-muted-steel mt-2 max-w-2xl font-sans">
            Двоколонкова специфікація голландського аукціону. Налаштуйте точні
            музейні параметри речі зліва та алгоритм падіння ціни справа.
          </p>
        </div>

        {!token ? (
          <div className="bg-pure-white border border-hairline-border p-4 flex flex-col gap-3">
            <div className="text-xs font-mono text-muted-steel">
              НЕОБХІДНА АВТОРИЗАЦІЯ ПРОДАВЦЯ
            </div>
            <div className="flex flex-col sm:flex-row gap-2">
              <input
                type="email"
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                placeholder="seller@veiling.test"
                className="border border-hairline-border px-2.5 py-1 text-xs font-mono rounded-none bg-pure-white"
              />
              <input
                type="password"
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                placeholder="Пароль"
                className="border border-hairline-border px-2.5 py-1 text-xs font-mono rounded-none bg-pure-white"
              />
              <Button
                variant="dark"
                size="sm"
                disabled={authLoading}
                onClick={handleQuickSellerLogin}
              >
                {authLoading ? "ВХІД..." : "ВХІД ПРОДАВЦЯ"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-xs font-mono text-carbon-pitch bg-pure-white border border-hairline-border px-3 py-2">
            <ShieldCheck className="w-4 h-4 text-electric-blue" />
            <span>СЕСІЯ ПРОДАВЦЯ АКТИВНА</span>
          </div>
        )}
      </div>

      {authError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 text-xs font-mono flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{authError}</span>
        </div>
      )}

      {submitError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 text-xs font-mono flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{submitError}</span>
        </div>
      )}

      <form onSubmit={handleSubmitLot}>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-7 space-y-8">
            <div className="bg-pure-white border border-hairline-border p-6 sm:p-8 space-y-6">
              <div className="border-b border-hairline-border pb-4 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono font-bold tracking-kicker uppercase text-muted-steel block">
                    01 / ПАРАМЕТРИ ЕКСПОНАТУ
                  </span>
                  <h2 className="text-xl font-bold tracking-tight text-carbon-pitch">
                    The Piece (Метадані раритету)
                  </h2>
                </div>
                <Badge variant="neutral">МУЗЕЙНИЙ СТАНДАРТ</Badge>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                    НАЗВА ЛОТА *
                  </label>
                  <input
                    type="text"
                    required
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder='наприклад: Бомбер Raf Simons AW01 "Riot! Riot! Riot!"'
                    className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      БРЕНД (ARCHIVE HOUSE) *
                    </label>
                    <input
                      type="text"
                      required
                      value={brand}
                      onChange={(e) => {
                        setBrand(e.target.value);
                        if (!designer || designer === brand) {
                          setDesigner(e.target.value);
                        }
                      }}
                      placeholder="Raf Simons"
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      ДИЗАЙНЕР
                    </label>
                    <input
                      type="text"
                      value={designer}
                      onChange={(e) => setDesigner(e.target.value)}
                      placeholder="Raf Simons"
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      СЕЗОН / ЕРА *
                    </label>
                    <input
                      type="text"
                      required
                      value={season}
                      onChange={(e) => setSeason(e.target.value)}
                      placeholder="Autumn/Winter"
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      РІК *
                    </label>
                    <input
                      type="number"
                      required
                      min={1900}
                      max={2100}
                      value={year}
                      onChange={(e) => setYear(Number(e.target.value))}
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      НАЗВА КОЛЕКЦІЇ
                    </label>
                    <input
                      type="text"
                      value={collectionName}
                      onChange={(e) => setCollectionName(e.target.value)}
                      placeholder='"Riot! Riot! Riot!"'
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      КАТЕГОРІЯ *
                    </label>
                    <select
                      value={category}
                      onChange={(e) =>
                        setCategory(e.target.value as LotCategory)
                      }
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    >
                      <option value="OUTERWEAR">OUTERWEAR (Верхній одяг)</option>
                      <option value="TOPS">TOPS (Светри, топи, сорочки)</option>
                      <option value="BOTTOMS">BOTTOMS (Штани, денім)</option>
                      <option value="FOOTWEAR">FOOTWEAR (Взуття)</option>
                      <option value="ACCESSORIES">ACCESSORIES (Аксесуари)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      ПІДКАТЕГОРІЯ *
                    </label>
                    <input
                      type="text"
                      required
                      value={subcategory}
                      onChange={(e) => setSubcategory(e.target.value)}
                      placeholder="Бомбер"
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      РОЗМІР НА БІРЦІ (TAGGED) *
                    </label>
                    <input
                      type="text"
                      required
                      value={taggedSize}
                      onChange={(e) => setTaggedSize(e.target.value)}
                      placeholder="50"
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      ФАКТИЧНА ПОСАДКА (FITS LIKE) *
                    </label>
                    <input
                      type="text"
                      required
                      value={fitsLike}
                      onChange={(e) => setFitsLike(e.target.value)}
                      placeholder="Oversized L"
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-sm font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                </div>
              </div>

              <div className="border-t border-hairline-border pt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch">
                    ТОЧНІ ЗАМІРИ В САНТИМЕТРАХ (JSONB)
                  </h3>
                  <span className="text-[10px] font-mono text-muted-steel">
                    ВИМІРЯНО НА ПЛОСКОСТІ (CM)
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      PIT TO PIT (ГРУДИ)
                    </label>
                    <input
                      type="number"
                      value={pitToPit || ""}
                      onChange={(e) => setPitToPit(Number(e.target.value))}
                      placeholder="62"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      LENGTH (ДОВЖИНА)
                    </label>
                    <input
                      type="number"
                      value={length || ""}
                      onChange={(e) => setLength(Number(e.target.value))}
                      placeholder="71"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      SHOULDERS (ПЛЕЧІ)
                    </label>
                    <input
                      type="number"
                      value={shoulders || ""}
                      onChange={(e) => setShoulders(Number(e.target.value))}
                      placeholder="54"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      SLEEVE (РУКАВ)
                    </label>
                    <input
                      type="number"
                      value={sleeve || ""}
                      onChange={(e) => setSleeve(Number(e.target.value))}
                      placeholder="66"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      WAIST (ПОЯС / ТАЛІЯ)
                    </label>
                    <input
                      type="number"
                      value={waist || ""}
                      onChange={(e) => setWaist(Number(e.target.value))}
                      placeholder="0"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      INSEAM (ВНУТР. ШОВ)
                    </label>
                    <input
                      type="number"
                      value={inseam || ""}
                      onChange={(e) => setInseam(Number(e.target.value))}
                      placeholder="0"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      HEM (НИЗ)
                    </label>
                    <input
                      type="number"
                      value={hem || ""}
                      onChange={(e) => setHem(Number(e.target.value))}
                      placeholder="58"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                </div>
              </div>

              <div className="border-t border-hairline-border pt-6 space-y-4">
                <h3 className="text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch">
                  СКЛАД ТКАНИН ТА МАТЕРІАЛІВ
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      ОСНОВА (OUTER) *
                    </label>
                    <input
                      type="text"
                      required
                      value={outerMaterial}
                      onChange={(e) => setOuterMaterial(e.target.value)}
                      placeholder="100% Cotton"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      ПІДКЛАДКА (LINING)
                    </label>
                    <input
                      type="text"
                      value={liningMaterial}
                      onChange={(e) => setLiningMaterial(e.target.value)}
                      placeholder="100% Cupro"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      ФУРНІТУРА (HARDWARE)
                    </label>
                    <input
                      type="text"
                      value={hardwareMaterial}
                      onChange={(e) => setHardwareMaterial(e.target.value)}
                      placeholder="Raccagni zippers"
                      className="w-full border border-hairline-border px-3 py-1.5 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                </div>
              </div>

              <div className="border-t border-hairline-border pt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch">
                    ОЦІНКА СТАНУ (1..10) ТА ДЕТАЛІ
                  </h3>
                  <span className="text-xs font-mono font-bold text-carbon-pitch">
                    {conditionRating} / 10
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setConditionRating(num)}
                      className={`flex-1 py-2 text-xs font-mono font-bold transition-colors rounded-none border ${
                        conditionRating === num
                          ? "bg-carbon-pitch text-pure-white border-carbon-pitch"
                          : "bg-pure-white text-muted-steel border-hairline-border hover:border-carbon-pitch"
                      }`}
                    >
                      {num}
                    </button>
                  ))}
                </div>
                <div>
                  <label className="block text-[10px] font-mono text-muted-steel mb-1">
                    ОПИС ПАТИНИ, ЗБЕРЕЖЕННЯ ТА НЮАНСІВ СТАНУ *
                  </label>
                  <textarea
                    required
                    rows={3}
                    value={conditionDetails}
                    onChange={(e) => setConditionDetails(e.target.value)}
                    placeholder="Детальний опис стану архіву..."
                    className="w-full border border-hairline-border p-3 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                  />
                </div>
              </div>

              <div className="border-t border-hairline-border pt-6 space-y-4">
                <h3 className="text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch">
                  ПОХОДЖЕННЯ ТА ДОСТАВКА
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      КРАЇНА ВИРОБНИЦТВА *
                    </label>
                    <input
                      type="text"
                      required
                      value={countryOfOrigin}
                      onChange={(e) => setCountryOfOrigin(e.target.value)}
                      placeholder="Бельгія"
                      className="w-full border border-hairline-border px-3.5 py-2 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-mono text-muted-steel mb-1">
                      ЛОКАЦІЯ ПРОДАВЦЯ *
                    </label>
                    <input
                      type="text"
                      required
                      value={sellerLocation}
                      onChange={(e) => setSellerLocation(e.target.value)}
                      placeholder="Амстердам, Нідерланди"
                      className="w-full border border-hairline-border px-3.5 py-2 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-[10px] font-mono text-muted-steel mb-1">
                    ПРОИСХОЖДЕННЯ (PROVENANCE NOTES)
                  </label>
                  <input
                    type="text"
                    value={provenanceNotes}
                    onChange={(e) => setProvenanceNotes(e.target.value)}
                    placeholder="Приватна колекція..."
                    className="w-full border border-hairline-border px-3.5 py-2 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-mono text-muted-steel mb-1">
                    ПРАВИЛА ДОСТАВКИ *
                  </label>
                  <input
                    type="text"
                    required
                    value={shippingNotes}
                    onChange={(e) => setShippingNotes(e.target.value)}
                    className="w-full border border-hairline-border px-3.5 py-2 text-xs font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                  />
                </div>
              </div>

              <div className="border-t border-hairline-border pt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-mono font-bold uppercase tracking-kicker text-carbon-pitch">
                      ФОТОГРАФІЇ РАРИТЕТУ (MINIO S3)
                    </h3>
                    <p className="text-[10px] font-mono text-muted-steel mt-0.5">
                      ПЕРШЕ ФОТО — ГОЛОВНИЙ РАКУРС. ПІДТРИМУЮТЬСЯ JPEG, PNG, WEBP.
                    </p>
                  </div>
                  <label
                    htmlFor={photoInputId}
                    className="cursor-pointer inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-mono font-bold tracking-wider uppercase bg-pure-white border border-hairline-border hover:border-carbon-pitch transition-colors rounded-none"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    <span>ДОДАТИ ФОТО</span>
                  </label>
                  <input
                    id={photoInputId}
                    type="file"
                    multiple
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>

                {photoError && (
                  <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs font-mono flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{photoError}</span>
                  </div>
                )}

                {isUploadingPhoto && (
                  <div className="p-3 bg-gallery-canvas border border-hairline-border text-xs font-mono text-carbon-pitch flex items-center space-x-2">
                    <div className="w-3.5 h-3.5 border-2 border-carbon-pitch border-t-transparent animate-spin" />
                    <span>ЗАВАНТАЖЕННЯ ЗОБРАЖЕННЯ В СХОВИЩЕ MINIO...</span>
                  </div>
                )}

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {photos.map((photo, idx) => (
                    <div
                      key={photo.id}
                      className="border border-hairline-border bg-gallery-canvas p-2 relative group"
                    >
                      <div className="aspect-square bg-neutral-200 overflow-hidden relative">
                        <img
                          src={photo.url}
                          alt={photo.caption}
                          className="w-full h-full object-cover"
                        />
                        <span className="absolute top-1.5 left-1.5 bg-carbon-pitch text-pure-white font-mono text-[10px] px-1.5 py-0.5 font-bold">
                          #{idx}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemovePhoto(photo.id)}
                          className="absolute top-1.5 right-1.5 bg-red-600 text-pure-white p-1 hover:bg-red-700 transition-colors"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <input
                        type="text"
                        value={photo.caption}
                        onChange={(e) =>
                          handleCaptionChange(photo.id, e.target.value)
                        }
                        placeholder="Підпис ракурсу..."
                        className="w-full mt-2 border border-hairline-border px-2 py-1 text-[11px] font-sans focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 space-y-8 sticky top-24">
            <div className="bg-pure-white border border-hairline-border p-6 sm:p-8 space-y-6">
              <div className="border-b border-hairline-border pb-4 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono font-bold tracking-kicker uppercase text-muted-steel block">
                    02 / ПАРАМЕТРИ ПАДІННЯ
                  </span>
                  <h2 className="text-xl font-bold tracking-tight text-carbon-pitch">
                    The Descent (Алгоритм спуску)
                  </h2>
                </div>
                <div className="w-3 h-3 bg-acid-lime" />
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch">
                      СТЕЛЯ ЦІНИ (OPENING CEILING) *
                    </label>
                    <span className="text-[10px] font-mono text-muted-steel">
                      СТАРТ
                    </span>
                  </div>
                  <div className="relative">
                    <input
                      type="number"
                      required
                      min={1}
                      value={startPrice}
                      onChange={(e) => setStartPrice(Number(e.target.value))}
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-lg font-mono font-bold focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                    <span className="absolute right-3.5 top-3 font-mono text-xs text-muted-steel">
                      ₴
                    </span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch">
                      ПІДЛОГА ЦІНИ (FLOOR LIMIT) *
                    </label>
                    <span className="text-[10px] font-mono text-muted-steel">
                      ЗУПИНКА
                    </span>
                  </div>
                  <div className="relative">
                    <input
                      type="number"
                      required
                      min={1}
                      value={floorPrice}
                      onChange={(e) => setFloorPrice(Number(e.target.value))}
                      className="w-full border border-hairline-border px-3.5 py-2.5 text-lg font-mono font-bold focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    />
                    <span className="absolute right-3.5 top-3 font-mono text-xs text-muted-steel">
                      ₴
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      КРОК ПАДІННЯ *
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        required
                        min={1}
                        value={stepAmount}
                        onChange={(e) => setStepAmount(Number(e.target.value))}
                        className="w-full border border-hairline-border px-3 py-2 text-sm font-mono font-bold focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                      />
                      <span className="absolute right-2.5 top-2.5 font-mono text-xs text-muted-steel">
                        ₴
                      </span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-mono font-bold uppercase tracking-wider text-carbon-pitch mb-1.5">
                      ІНТЕРВАЛ *
                    </label>
                    <select
                      value={intervalSeconds}
                      onChange={(e) =>
                        setIntervalSeconds(Number(e.target.value))
                      }
                      className="w-full border border-hairline-border px-3 py-2 text-sm font-mono focus:outline-none focus:border-carbon-pitch rounded-none bg-pure-white"
                    >
                      <option value={30}>30 сек</option>
                      <option value={60}>60 сек (1 хв)</option>
                      <option value={120}>120 сек (2 хв)</option>
                      <option value={300}>300 сек (5 хв)</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-gallery-canvas border border-hairline-border space-y-3 font-mono">
                <div className="text-[10px] font-bold tracking-kicker uppercase text-muted-steel">
                  МАТЕМАТИЧНИЙ РОЗРАХУНОК СПУСКУ
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-muted-steel block">СУМА СПУСКУ:</span>
                    <span className="font-bold text-carbon-pitch">
                      {totalDrop.toLocaleString()} ₴
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-steel block">КІЛЬКІСТЬ КРОКІВ:</span>
                    <span className="font-bold text-carbon-pitch">
                      {totalSteps} кроків
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-steel block">ЧАС СПУСКУ:</span>
                    <span className="font-bold text-carbon-pitch">
                      {totalHours}г {remainingMinutes}хв
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-steel block">МАКС. ЕКОНОМІЯ:</span>
                    <span className="font-bold text-electric-blue">
                      -{maxSavingsPct}%
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-hairline-border">
                  <div className="text-[10px] font-bold tracking-kicker uppercase text-muted-steel mb-2">
                    ПРОЕКЦІЯ ГРАФІКА СПУСКУ
                  </div>
                  <div className="max-h-36 overflow-y-auto space-y-1 text-[11px]">
                    {scheduleRows.map((row) => (
                      <div
                        key={row.step}
                        className="flex items-center justify-between py-0.5 border-b border-hairline-border/60"
                      >
                        <span className="text-muted-steel">
                          #{row.step} ({row.time})
                        </span>
                        <span className="font-bold">
                          {row.price.toLocaleString()} ₴
                        </span>
                        <span className="text-electric-blue">
                          -{row.savings}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="border border-hairline-border p-4 bg-pure-white space-y-3">
                <div className="flex items-center justify-between text-xs font-mono font-bold uppercase text-carbon-pitch">
                  <div className="flex items-center space-x-1.5">
                    <Eye className="w-3.5 h-3.5 text-muted-steel" />
                    <span>ПРЕВ'Ю КАРТКИ ЛОТА</span>
                  </div>
                  <Badge variant="lime">SCHEDULED</Badge>
                </div>

                <div className="aspect-[4/3] bg-gallery-canvas overflow-hidden border border-hairline-border flex items-center justify-center relative">
                  {photos.length > 0 ? (
                    <img
                      src={photos[0].url}
                      alt="Прев'ю"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-xs font-mono text-muted-steel">
                      НЕМАЄ ФОТОГРАФІЇ
                    </div>
                  )}
                  <div className="absolute bottom-2 left-2 bg-carbon-pitch/90 text-pure-white text-[10px] font-mono px-2 py-0.5">
                    {brand} · {year}
                  </div>
                </div>

                <div>
                  <h4 className="font-bold text-sm text-carbon-pitch line-clamp-1">
                    {title || "Назва раритету"}
                  </h4>
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-hairline-border font-mono">
                    <div>
                      <span className="text-[10px] text-muted-steel block">
                        ПОТОЧНА ЦІНА
                      </span>
                      <span className="text-lg font-extrabold text-carbon-pitch">
                        {startPrice.toLocaleString()} ₴
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-muted-steel block">
                        ПІДЛОГА
                      </span>
                      <span className="text-xs text-muted-steel">
                        {floorPrice.toLocaleString()} ₴
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                disabled={isSubmitting}
                className="w-full py-4 text-sm font-bold tracking-wider"
              >
                {isSubmitting
                  ? "ПУБЛІКАЦІЯ ТА СТАРТ СПУСКУ..."
                  : "ОПУБЛІКУВАТИ ТА РОЗПОЧАТИ СПУСК"}
              </Button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};
