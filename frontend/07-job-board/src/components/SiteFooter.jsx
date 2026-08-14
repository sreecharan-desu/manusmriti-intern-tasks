import { useEffect, useState } from "react";

export function SiteFooter({ note }) {
  const [timeStr, setTimeStr] = useState(null);

  useEffect(() => {
    const update = () => {
      setTimeStr(
        new Date()
          .toLocaleTimeString("en-US", {
            timeZone: "Asia/Kolkata",
            hour: "numeric",
            minute: "2-digit",
            second: "2-digit",
            hour12: true,
          })
          .toLowerCase(),
      );
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <footer className="site-footer">
      <p>
        {note}
        {timeStr ? (
          <>
            {" "}
            · <span className="clock">{timeStr} IST</span>
          </>
        ) : null}
      </p>
    </footer>
  );
}
