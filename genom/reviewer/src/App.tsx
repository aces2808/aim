import { useEffect, useRef, useState } from 'react';

export default function App() {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isBirthday, setIsBirthday] = useState(false);

  useEffect(() => {
    const checkBirthday = () => {
      try {
        const iframeDoc = iframeRef.current?.contentDocument;
        if (iframeDoc) {
          const bodyText = iframeDoc.body.innerText || '';
          if (bodyText.includes('Happy Birthday Jen Subang')) {
            setIsBirthday(true);
          }

          const searchInput = iframeDoc.querySelector(
            'input[type="search"], input[placeholder*="search" i]'
          ) as HTMLInputElement;
          if (searchInput) {
            const handleSearch = () => {
              if (searchInput.value.includes('Happy Birthday Jen Subang')) {
                setIsBirthday(true);
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

    const timer = setTimeout(checkBirthday, 1000);
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
    </>
  );
}
