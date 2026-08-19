import { useEffect, useRef, useState } from 'react';

export default function App() {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isBirthday, setIsBirthday] = useState(false);
  const [isWedding, setIsWedding] = useState(false);

  useEffect(() => {
    const checkCelebration = () => {
      try {
        const iframeDoc = iframeRef.current?.contentDocument;
        if (iframeDoc) {
          const bodyText = iframeDoc.body.innerText || '';
          if (bodyText.includes('Happy Birthday Jen Subang')) {
            setIsBirthday(true);
          }
          if (bodyText.includes('Congrats and Best Wishes Emylea')) {
            setIsWedding(true);
          }

          const searchInput = iframeDoc.querySelector(
            'input[type="search"], input[placeholder*="search" i]'
          ) as HTMLInputElement;
          if (searchInput) {
            const handleSearch = () => {
              if (searchInput.value.includes('Happy Birthday Jen Subang')) {
                setIsBirthday(true);
              }
              if (searchInput.value.includes('Congrats and Best Wishes Emylea')) {
                setIsWedding(true);
              }
            };
            searchInput.addEventListener('input', handleSearch);
            return () => searchInput.removeEventListener('input', handleSearch);
          }
        }
      } catch (e) {
        // Cross-origin iframe, silently fail
      }
    };

    const timer = setTimeout(checkCelebration, 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <iframe
        ref={iframeRef}
        src="/notes/index.html"
        style={{ width: '100%', height: '100%', border: 'none', display: 'block' }}
        title="MIB Reviewer"
        loading="lazy"
      />
      {isBirthday && (
        <div className="birthday-celebration">
          <div className="confetti"></div>
          <div className="confetti"></div>
          <div className="confetti"></div>
          <div className="confetti"></div>
          <div className="confetti"></div>

          <div className="birthday-cake">
            <div className="balloon balloon-1"></div>
            <div className="balloon balloon-2"></div>
            <div className="balloon balloon-3"></div>

            <div className="cake-layer cake-bottom"></div>
            <div className="cake-layer cake-middle"></div>
            <div className="cake-layer cake-top"></div>
            <div className="candle"></div>
          </div>
        </div>
      )}
      {isWedding && (
        <div className="wedding-celebration">
          <div className="rose-petal"></div>
          <div className="rose-petal"></div>
          <div className="rose-petal"></div>
          <div className="rose-petal"></div>
          <div className="rose-petal"></div>

          <div className="wedding-display">
            <div className="bride">👰</div>
            <div className="wedding-cake-w">
              <div className="cake-layer-w cake-bottom-w"></div>
              <div className="cake-layer-w cake-middle-w"></div>
              <div className="cake-layer-w cake-top-w"></div>
              <div className="heart heart-1">💕</div>
              <div className="heart heart-2">💕</div>
            </div>
            <div className="groom">🤵</div>
          </div>
        </div>
      )}
    </>
  );
}
