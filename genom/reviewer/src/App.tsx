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
        </div>
      )}
    </>
  );
}
