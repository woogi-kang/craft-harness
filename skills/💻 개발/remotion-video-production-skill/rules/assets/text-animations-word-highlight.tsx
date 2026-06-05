import React from "react";

export function WordHighlight({ children }: { children: React.ReactNode }) {
  return <mark>{children}</mark>;
}
