import React, { useState } from "react";
import { LotImage } from "../../types";
import { Search } from "lucide-react";

interface PhotoGalleryProps {
  images: LotImage[];
  title: string;
}

export const PhotoGallery: React.FC<PhotoGalleryProps> = ({ images, title }) => {
  const sortedImages =
    images && images.length > 0
      ? [...images].sort((a, b) => a.sort_order - b.sort_order)
      : [];

  const [activeIndex, setActiveIndex] = useState<number>(0);
  const [isZooming, setIsZooming] = useState<boolean>(false);
  const [zoomPos, setZoomPos] = useState<{ x: number; y: number }>({ x: 50, y: 50 });

  const activeImage = sortedImages[activeIndex] || null;

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
    const y = Math.max(0, Math.min(100, ((e.clientY - rect.top) / rect.height) * 100));
    setZoomPos({ x, y });
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (e.touches.length === 0) {
      return;
    }
    const touch = e.touches[0];
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.max(0, Math.min(100, ((touch.clientX - rect.left) / rect.width) * 100));
    const y = Math.max(0, Math.min(100, ((touch.clientY - rect.top) / rect.height) * 100));
    setZoomPos({ x, y });
  };

  return (
    <div className="space-y-4 select-none">
      <div
        className="relative aspect-square bg-gallery-canvas border border-hairline-border overflow-hidden cursor-crosshair group"
        onMouseEnter={() => setIsZooming(true)}
        onMouseLeave={() => setIsZooming(false)}
        onMouseMove={handleMouseMove}
        onTouchStart={() => setIsZooming(true)}
        onTouchEnd={() => setIsZooming(false)}
        onTouchMove={handleTouchMove}
      >
        {activeImage ? (
          <>
            <img
              src={activeImage.image_url}
              alt={activeImage.caption || title}
              onError={(e) => {
                const target = e.currentTarget as HTMLImageElement;
                const filename = activeImage.image_url.split("/").pop();
                if (filename && !target.src.includes(`/lots/${filename}`)) {
                  target.src = `/lots/${filename}`;
                }
              }}
              className={`w-full h-full object-cover object-center transition-opacity duration-200 ${
                isZooming ? "opacity-0" : "opacity-100"
              }`}
            />
            {isZooming && (
              <div
                className="absolute inset-0 bg-no-repeat pointer-events-none"
                style={{
                  backgroundImage: `url(${activeImage.image_url})`,
                  backgroundPosition: `${zoomPos.x}% ${zoomPos.y}%`,
                  backgroundSize: "250%",
                }}
              />
            )}
            <div className="absolute top-3 right-3 bg-carbon-pitch/80 backdrop-blur-sm text-pure-white px-2.5 py-1 text-[10px] font-mono tracking-kicker uppercase flex items-center gap-1.5 border border-pure-white/10 pointer-events-none">
              <Search className="w-3 h-3 text-acid-lime" />
              <span>{isZooming ? "ЛУПА АКТИВНА (2.5x)" : "НАВЕДІТЬ ДЛЯ ЛУПИ"}</span>
            </div>
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center p-8 text-center bg-gallery-canvas">
            <span className="text-xs font-mono text-muted-steel uppercase tracking-kicker">
              {title}
            </span>
          </div>
        )}
      </div>

      {activeImage && activeImage.caption && (
        <div className="text-xs font-mono text-muted-steel uppercase tracking-kicker px-1">
          РАКУРС: {activeImage.caption}
        </div>
      )}

      {sortedImages.length > 1 && (
        <div className="grid grid-cols-4 sm:grid-cols-6 gap-3">
          {sortedImages.map((img, idx) => {
            const isCurrent = idx === activeIndex;
            return (
              <button
                key={img.id || idx}
                type="button"
                onClick={() => setActiveIndex(idx)}
                className={`relative aspect-square bg-gallery-canvas border overflow-hidden transition-colors ${
                  isCurrent
                    ? "border-carbon-pitch ring-1 ring-carbon-pitch"
                    : "border-hairline-border hover:border-carbon-pitch/50 opacity-70 hover:opacity-100"
                }`}
              >
                <img
                  src={img.image_url}
                  alt={img.caption || `${title} angle ${idx + 1}`}
                  onError={(e) => {
                    const target = e.currentTarget as HTMLImageElement;
                    const filename = img.image_url.split("/").pop();
                    if (filename && !target.src.includes(`/lots/${filename}`)) {
                      target.src = `/lots/${filename}`;
                    }
                  }}
                  className="w-full h-full object-cover object-center"
                />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
