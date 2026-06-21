import { useEffect } from "react";
import { on, off } from "../services/socket";

export function useSocketEvent(type, handler) {
  useEffect(() => {
    on(type, handler);
    return () => off(type);
  }, [type, handler]);
}
